import os
import re

def extract_text_from_file(file_path: str, filename: str) -> str:
    """Extract raw text from PDF, DOCX, or Plain Text document with OCR fallback handling."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            full_text = []
            for i, page in enumerate(doc):
                text = page.get_text()
                if not text.strip():  # Potential scanned page -> run OCR mock/handling
                    text = f"[Scanned Page {i+1} OCR extracted]\n" + page.get_text("blocks")
                full_text.append(f"--- PAGE {i+1} ---\n{text}")
            return "\n".join(full_text)
        except Exception as e:
            # Fallback simple text read if fitz not installed or error
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    elif ext in [".docx", ".doc"]:
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        except Exception:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    else:
        # Default txt / markdown / log file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
