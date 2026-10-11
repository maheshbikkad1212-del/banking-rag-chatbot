# 🏦 Banking Smart Document Understanding Chatbot (Advanced RAG)

A production-grade **Retrieval-Augmented Generation (RAG) Architecture** designed for regulated banking environments. Grounded strictly in official regulatory policies, loan manuals, and interest rate schedules to guarantee zero hallucination and complete auditability.

---

## 🌟 Key Architectural Features

### 1. Ingestion Pipeline (`backend/app/ingestion/`)
- **Multi-Format Parsing**: PyMuPDF loader for native PDFs, `python-docx` for Word manuals, with OCR text extraction fallback.
- **Noise Cleanup & Normalization**: Strips header/footer artifacts, page numbering boilerplate, and fixes OCR errors.
- **Recursive Token Chunking**: 500–600 token target chunk size with 50–100 token overlap to preserve semantic boundaries across paragraphs and policy tables.
- **Metadata Enrichment**: Tagged with Document Name, Authority (e.g., RBI, Credit Risk Committee), Version, Effective Date, and Page Numbers.

### 2. Dense + Sparse Hybrid Search (`backend/app/vectorstore/`)
- **Dense Vector Search**: Semantic vectorization using `all-MiniLM-L6-v2` (`sentence-transformers`).
- **Sparse BM25 Keyword Search**: Exact term frequency matching for numeric values, monetary figures, and policy rules (e.g., `7.25%`, `₹30 Lakhs`, `90% LTV`).
- **Reciprocal Rank Fusion (RRF)**: Combines dense & sparse scoring with metadata filtering.

### 3. Multi-Level Caching (`backend/app/rag/cache.py`)
- **L1 Cache**: Normalized Query String Cache.
- **L2 Cache**: Hybrid Document Retrieval Chunk Cache.
- **L3 Cache**: Full Synthesized Response & Verified Answer Cache.

### 4. Advanced RAG Components
- **Query Processing**: Intent Detection (Loan Eligibility, FD Interest Rates, KYC Guidelines, Regulatory Capital), Query Normalization & Expansion.
- **Max Marginal Relevance (MMR)**: Eliminates redundant chunks, maximizing context coverage diversity.
- **Corrective RAG (CRAG)**: Evaluates context relevance score and coverage; triggers query expansion re-retrieval if context is ambiguous or insufficient.
- **Authority & Recency Re-Ranker**: Priority boosting for RBI Master Directions and newest 2024–2025 circulars.
- **Post-Generation Numerical Validation Guardrail**: Validates interest rates, percentages, and monetary amounts against source context chunks to prevent numeric hallucination.
- **Strict Context-Bounded Generator**: Answers exclusively from context with page & document citations.

---

## 📁 Directory Structure

```
banking-rag-system/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI Application & REST Endpoints
│   │   ├── config.py                # Environment & RAG Hyperparameters
│   │   ├── ingestion/               # Extraction, Cleaning, Chunking, Metadata
│   │   ├── vectorstore/             # Embeddings, BM25, Hybrid Search
│   │   ├── rag/                     # Cache, Intent, Memory, MMR, CRAG, Re-ranker, Guardrail, Generator
│   │   └── sample_docs/             # Pre-loaded RBI Loan Policy, FD Rates 2025, KYC & Basel III docs
│   ├── requirements.txt             # Python Dependencies
│   └── run.py                       # Uvicorn Server Starter
└── frontend/
    ├── index.html                   # HTML Entrypoint
    ├── vite.config.js               # Vite Config with Backend API Proxy
    ├── package.json                 # Node.js Dependencies
    └── src/
        ├── main.jsx                 # React Entrypoint
        ├── App.jsx                  # Main Layout & State Management
        ├── index.css                # Glassmorphic Styling & Animations
        ├── api/client.js            # REST API Client
        └── components/              # Navbar, ChatContainer, CitationModal, PipelineVisualizer, DocumentManager
```

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Launch Backend Server
```bash
cd backend
pip install -r requirements.txt
python run.py
```
> Server will start at `http://localhost:8000`. Swagger API docs available at `http://localhost:8000/docs`.

### 2. Launch Frontend Application
```bash
cd frontend
npm install
npm run dev
```
> Open `http://localhost:3000` in your web browser.

---

## 🧪 Testing the RAG Pipeline

1. **Loan Eligibility Query**:
   > *"What is the maximum LTV ratio for home loans up to ₹30 Lakhs under RBI rules?"*
   - **Expected Output**: 90% LTV with 10% borrower margin. Citation: *Master Direction on Home & Personal Loan Eligibility Guidelines*, Page 1.

2. **Fixed Deposit Interest Rate Query**:
   > *"What is the FD interest rate for senior citizens on a 1-year deposit?"*
   - **Expected Output**: 7.25% p.a. (General Public 6.75% + 0.50% Senior Citizen Bonus). Citation: *Retail Fixed Deposit Interest Rates Schedule (Q1 2025)*.

3. **KYC & NRI Account Onboarding Query**:
   > *"What mandatory documents are required to open an NRE account?"*
   - **Expected Output**: Valid Indian Passport, Employment Visa/Work Permit, Overseas Address Proof, PAN/Form 60, FATCA TIN. Citation: *Master Guidelines on KYC & NRI Account Onboarding*.

4. **Numerical Guardrail & CRAG Verification**:
   - Inspect the **RAG Execution Traces** side panel in the frontend UI to observe Intent Classification, Hybrid Search Chunks, CRAG Status (CORRECT/AMBIGUOUS), and Numerical Guardrail status!
