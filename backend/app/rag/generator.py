import re
from typing import List, Dict, Any
from app.config import settings

SYSTEM_PROMPT = """You are an expert Banking Policy Assistant.
Your primary task is to answer policy-related questions strictly using the authorized banking documents provided below.

STRICT REGULATION RULES:
1. Base your answer EXCLUSIVELY on the provided Context Chunks. Do NOT use outside knowledge or training data assumptions.
2. If the exact answer is not present in the context chunks, state: "I cannot locate this information in the authorized banking policy documents."
3. Cite the Document Name, Section, and Page Number for all factual claims or numeric figures.
4. Do NOT alter any interest rates, percentages, tenure limits, or numeric amounts.
"""

def generate_rag_response(
    query: str,
    context_chunks: List[Dict[str, Any]],
    intent: str
) -> str:
    """Generates context-bounded answer with citations using Groq API, OpenAI, or synthesis fallback."""
    if not context_chunks:
        return "I cannot locate relevant information in the authorized banking policy documents to answer your query. Please refer to official banking manuals or rephrase your question."

    # Format context chunks with citation labels
    context_str = ""
    for i, chunk in enumerate(context_chunks, 1):
        meta = chunk.get("metadata", {})
        doc_name = meta.get("doc_name", chunk.get("source_filename", "Document"))
        page = chunk.get("page_number", meta.get("page_number", 1))
        auth = meta.get("authority", "Official Policy")
        eff_date = meta.get("effective_date", "2024-2025")
        
        context_str += f"\n--- [CONTEXT CHUNK {i}] ---\n"
        context_str += f"Source Document: {doc_name}\n"
        context_str += f"Authority: {auth} | Effective Date: {eff_date} | Page: {page}\n"
        context_str += f"Content:\n{chunk['text']}\n"

    prompt = f"User Question: {query}\n\nContext Documents:\n{context_str}\n\nProvide a clear, detailed, policy-compliant response with document citations."

    # 1. Primary: Groq API Inference
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip() and not settings.GROQ_API_KEY.startswith("your_"):
        models_to_try = [
            settings.GROQ_MODEL_NAME,
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen-2.5-72b-instruct",
            "gemma2-9b-it",
            "llama-3.2-3b-preview",
            "llama-3.2-1b-preview"
        ]
        # Deduplicate while preserving order
        candidate_models = list(dict.fromkeys(models_to_try))


        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            for model_name in candidate_models:
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0
                    )
                    print(f"[Generator] Successfully generated answer via Groq API ({model_name})")
                    return response.choices[0].message.content
                except Exception as m_err:
                    print(f"[Generator] Groq model '{model_name}' error: {m_err}. Trying next candidate...")
        except Exception as e:
            print(f"[Generator] Groq API client initialization error: {e}. Falling back to context synthesis engine.")


    # # 2. Secondary: OpenAI / Azure OpenAI API
    # if settings.OPENAI_API_KEY or settings.AZURE_OPENAI_KEY:
    #     try:
    #         import openai
    #         if settings.AZURE_OPENAI_KEY:
    #             client = openai.AzureOpenAI(
    #                 api_key=settings.AZURE_OPENAI_KEY,
    #                 azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    #                 api_version="2024-02-15-preview"
    #             )
    #         else:
    #             client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    #         response = client.chat.completions.create(
    #             model=settings.MODEL_NAME,
    #             messages=[
    #                 {"role": "system", "content": SYSTEM_PROMPT},
    #                 {"role": "user", "content": prompt}
    #             ],
    #             temperature=0.0
    #         )
    #         return response.choices[0].message.content
    #     except Exception as e:
    #         print(f"[Generator] OpenAI call error ({e}).")

    # 3. Reliable Offline Context-Grounded Synthesizer Engine
    return _context_grounded_synthesis(query, context_chunks, intent)

def _context_grounded_synthesis(
    query: str,
    chunks: List[Dict[str, Any]],
    intent: str
) -> str:
    """Synthesizes clean, beautifully structured, precise query-relevant cited Markdown responses."""
    if not chunks:
        return f"I cannot locate information regarding '{query}' in the authorized banking policy documents."

    query_words = set(re.findall(r'\w+', query.lower()))
    stop_words = {"what", "is", "a", "an", "the", "for", "of", "and", "or", "in", "on", "to", "with", "are", "how", "do", "does", "should", "can", "what's"}
    query_keywords = {w for w in query_words if w not in stop_words and len(w) > 1}

    relevant_sentences = []
    seen = set()

    for chunk in chunks:
        meta = chunk.get("metadata", {})
        doc_name = meta.get("doc_name", chunk.get("source_filename", "Policy Document"))
        page = chunk.get("page_number", meta.get("page_number", 1))
        
        # Clean raw text: remove page header markers and bullet artifacts
        raw_text = chunk["text"]
        raw_text = re.sub(r'--- PAGE \d+ ---', '', raw_text)
        raw_text = re.sub(r'(\s*•)+', ' ', raw_text)
        raw_text = re.sub(r'(?i)11\.\s+Example Customer Questions.*', '', raw_text)  # Strip example test questions

        # Split into sentences or term definition clauses
        # Splitting on periods, newlines, or term headers like "OTP ", "PIN ", "EMI "
        sentences = re.split(r'(?<=[.!?])\s+|\n+|(?:(?<=[a-z0-9])\s+(?=[A-Z]{2,10}\b))', raw_text)

        for sent in sentences:
            sent_clean = re.sub(r'\s+', ' ', sent).strip()
            if not sent_clean or len(sent_clean) < 10:
                continue
            if sent_clean.startswith("===") or sent_clean.startswith("Document") or sent_clean.startswith("Authority"):
                continue

            sent_lower = sent_clean.lower()
            matches = sum(1 for kw in query_keywords if kw in sent_lower)
            
            if matches > 0 and sent_clean not in seen:
                seen.add(sent_clean)
                relevant_sentences.append({
                    "text": sent_clean,
                    "matches": matches,
                    "doc_name": doc_name,
                    "page": page,
                    "chunk": chunk
                })

    # Sort sentences by keyword match density descending
    relevant_sentences.sort(key=lambda x: x["matches"], reverse=True)

    if not relevant_sentences:
        return f"I cannot locate specific details regarding **'{query}'** in the authorized banking policy documents. Please verify your query or check the uploaded document."

    top_match = relevant_sentences[0]
    doc_name = top_match["doc_name"]
    meta = top_match["chunk"].get("metadata", {})
    auth = meta.get("authority", "General Banking Policy")
    eff_date = meta.get("effective_date", "2024-2025")
    page = top_match["page"]

    output = f"Based strictly on **{doc_name}** (Issued by: *{auth}*, Effective: *{eff_date}*):\n\n"

    # Select top 3-4 most relevant sentences matching the query
    top_sents = relevant_sentences[:4]
    
    for s in top_sents:
        clean_line = s["text"]
        # Format term definitions cleanly if pattern matches 'TERM Definition'
        term_match = re.match(r'^([A-Z0-9\s]{2,25})\s+([A-Z][a-z].*)', clean_line)
        if term_match and not clean_line.startswith("http") and not clean_line.startswith("Note"):
            term_name = term_match.group(1).strip()
            term_desc = term_match.group(2).strip()
            output += f"- **{term_name}**: {term_desc}\n\n"
        elif ":" in clean_line[:30]:
            parts = clean_line.split(":", 1)
            output += f"- **{parts[0].strip()}**: {parts[1].strip()}\n\n"
        else:
            output += f"- {clean_line}\n\n"

    output += f"> **Citation**: *{doc_name}*, Page {page}. Policy Authority: {auth}. Version {meta.get('version', '1.0')}."
    return output.strip()




