import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


from app.config import settings
from app.ingestion.extractors import extract_text_from_file
from app.ingestion.cleaner import clean_and_normalize_text
from app.ingestion.chunker import recursive_token_chunking
from app.ingestion.metadata import extract_document_metadata
from app.vectorstore.hybrid_store import vector_store
from app.rag.cache import cache_system
from app.rag.query_processor import process_query
from app.rag.memory import conversation_memory
from app.rag.mmr import apply_mmr
from app.rag.crag import crag_evaluator
from app.rag.reranker import rerank_chunks
from app.rag.validator import validate_numerical_accuracy
from app.rag.generator import generate_rag_response

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Advanced RAG Backend for Banking Smart Document Understanding"
)

# Enable CORS for frontend UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    authority_filter: Optional[str] = None
    use_cache: bool = True

class ChatResponse(BaseModel):
    query: str
    answer: str
    intent: str
    intent_confidence: float
    crag_evaluation: Dict[str, Any]
    numerical_validation: Dict[str, Any]
    cache_hit_level: Optional[str]
    citations: List[Dict[str, Any]]

@app.on_event("startup")
def startup_event():
    """Seed sample banking policy documents on startup."""
    print("[Startup] Seeding sample banking policy documents...")
    seed_sample_documents()

def seed_sample_documents():
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    if not os.path.exists(sample_dir):
        return

    for fname in os.listdir(sample_dir):
        fpath = os.path.join(sample_dir, fname)
        if os.path.isfile(fpath):
            raw_text = extract_text_from_file(fpath, fname)
            cleaned_text = clean_and_normalize_text(raw_text)
            meta = extract_document_metadata(cleaned_text, fname)
            
            raw_chunks = recursive_token_chunking(
                cleaned_text,
                chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
                chunk_overlap_tokens=settings.CHUNK_OVERLAP_TOKENS
            )
            
            final_chunks = []
            for chunk in raw_chunks:
                chunk["metadata"] = meta
                chunk["source_filename"] = fname
                final_chunks.append(chunk)

            vector_store.add_chunks(final_chunks)

    print(f"[Startup] Ingestion completed. Indexed {len(vector_store.chunks)} total chunks.")

@app.get("/")
def root():
    """Redirect root path to interactive API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "vector_store_chunks": len(vector_store.chunks),
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "cache_stats": cache_system.stats
    }

@app.post("/api/seed")
def trigger_seed():
    vector_store.clear()
    cache_system.clear()
    seed_sample_documents()
    return {"message": "Successfully re-seeded default banking documents", "chunks": len(vector_store.chunks)}

@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    # 1. Multi-Level Cache Check (L3: Final Response)
    if req.use_cache:
        cached_l3 = cache_system.get_l3_response(query)
        if cached_l3:
            cached_l3["cache_hit_level"] = "L3 Response Cache"
            return cached_l3

    # 2. Query Contextualization & Processing
    contextualized_query = conversation_memory.contextualize_query(query)
    q_proc = process_query(contextualized_query)
    intent = q_proc["intent"]
    confidence = q_proc["intent_confidence"]

    # 3. Hybrid Retrieval (Dense + Sparse BM25)
    retrieved_chunks = vector_store.hybrid_search(
        query=contextualized_query,
        top_k=settings.TOP_K_DENSE,
        metadata_filters={"authority": req.authority_filter} if req.authority_filter else None
    )

    # 4. Corrective RAG (CRAG) Evaluation
    crag_result = crag_evaluator.evaluate_retrieval(contextualized_query, retrieved_chunks)

    # Fallback re-retrieval if CRAG evaluation signal is AMBIGUOUS or INCORRECT
    if crag_result["evaluation_status"] in ["AMBIGUOUS", "INCORRECT"]:
        expanded_query = " ".join(q_proc["expansions"])
        fallback_chunks = vector_store.hybrid_search(query=expanded_query, top_k=settings.TOP_K_DENSE)
        if fallback_chunks:
            retrieved_chunks = fallback_chunks
            crag_result = crag_evaluator.evaluate_retrieval(expanded_query, retrieved_chunks)
            crag_result["recommendation"] += " (Executed Corrective Re-retrieval via Query Expansion)"

    # 5. Max Marginal Relevance (MMR) Diversification
    mmr_chunks = apply_mmr(
        query=contextualized_query,
        chunks=retrieved_chunks,
        top_k=settings.TOP_K_FINAL,
        lambda_param=settings.MMR_LAMBDA
    )

    # 6. Authority & Recency Re-ranking
    final_chunks = rerank_chunks(mmr_chunks, contextualized_query)

    # 7. LLM Response Synthesis
    answer = generate_rag_response(contextualized_query, final_chunks, intent)

    # 8. Post-Generation Numerical Validation Guardrail
    num_validation = validate_numerical_accuracy(final_chunks, answer)

    # 9. Format Citations
    citations = []
    for chunk in final_chunks:
        meta = chunk.get("metadata", {})
        citations.append({
            "doc_name": meta.get("doc_name", chunk.get("source_filename")),
            "authority": meta.get("authority", "Banking Guideline"),
            "effective_date": meta.get("effective_date", "2024-2025"),
            "page_number": chunk.get("page_number", meta.get("page_number", 1)),
            "version": meta.get("version", "1.0"),
            "snippet": chunk["text"][:250] + "...",
            "score": chunk.get("reranked_score", chunk.get("score", 0.0))
        })

    response_payload = {
        "query": query,
        "answer": answer,
        "intent": intent,
        "intent_confidence": confidence,
        "crag_evaluation": crag_result,
        "numerical_validation": num_validation,
        "cache_hit_level": None,
        "citations": citations
    }

    # Update Conversation Memory & Multi-Level Cache
    conversation_memory.add_turn(query, answer)
    cache_system.set_l3_response(query, response_payload)

    return response_payload

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    temp_path = os.path.join(os.path.dirname(__file__), "uploaded_" + filename)
    
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    raw_text = extract_text_from_file(temp_path, filename)
    cleaned_text = clean_and_normalize_text(raw_text)
    meta = extract_document_metadata(cleaned_text, filename)
    
    chunks = recursive_token_chunking(
        cleaned_text,
        chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
        chunk_overlap_tokens=settings.CHUNK_OVERLAP_TOKENS
    )

    final_chunks = []
    for c in chunks:
        c["metadata"] = meta
        c["source_filename"] = filename
        final_chunks.append(c)

    vector_store.add_chunks(final_chunks)

    # Invalidate cache & memory so uploaded document queries reflect immediately
    cache_system.clear()
    conversation_memory.clear()

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {
        "filename": filename,
        "status": "success",
        "chunks_indexed": len(final_chunks),
        "metadata": meta
    }

@app.get("/api/documents")
def list_documents():
    docs = {}
    for chunk in vector_store.chunks:
        meta = chunk.get("metadata", {})
        doc_name = meta.get("doc_name", chunk.get("source_filename", "Unknown"))
        if doc_name not in docs:
            docs[doc_name] = {
                "doc_name": doc_name,
                "authority": meta.get("authority", "N/A"),
                "effective_date": meta.get("effective_date", "N/A"),
                "version": meta.get("version", "N/A"),
                "chunk_count": 0
            }
        docs[doc_name]["chunk_count"] += 1
    return list(docs.values())

@app.get("/api/cache/stats")
def get_cache_stats():
    return cache_system.stats

@app.delete("/api/cache/clear")
def clear_cache():
    cache_system.clear()
    return {"message": "L1, L2, and L3 caches cleared successfully"}
