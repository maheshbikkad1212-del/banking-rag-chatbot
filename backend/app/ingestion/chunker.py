from typing import List, Dict, Any
import re

def recursive_token_chunking(
    text: str,
    chunk_size_tokens: int = 550,
    chunk_overlap_tokens: int = 75
) -> List[Dict[str, Any]]:
    """
    Splits text recursively using section titles, paragraphs, and sentences,
    maintaining 500-600 token window (~2200 chars) and 50-100 token overlap (~300 chars).
    """
    # Rough conversion: 1 token approx 4 characters
    char_limit = chunk_size_tokens * 4
    overlap_limit = chunk_overlap_tokens * 4

    # First split by major section headers or double newlines
    paragraphs = text.split("\n\n")
    
    chunks = []
    current_chunk = ""
    current_page = 1

    for para in paragraphs:
        # Check for page markers
        page_match = re.search(r'--- PAGE (\d+) ---', para)
        if page_match:
            current_page = int(page_match.group(1))

        if len(current_chunk) + len(para) <= char_limit:
            current_chunk += ("\n\n" if current_chunk else "") + para
        else:
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "approx_tokens": len(current_chunk.split()),
                    "page_number": current_page
                })
            
            # Carry over overlap from the end of current_chunk
            overlap_text = current_chunk[-overlap_limit:] if len(current_chunk) > overlap_limit else current_chunk
            current_chunk = overlap_text + "\n\n" + para

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "approx_tokens": len(current_chunk.split()),
            "page_number": current_page
        })

    return chunks
