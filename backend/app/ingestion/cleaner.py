import re

def clean_and_normalize_text(text: str) -> str:
    """Removes noise, running headers/footers, excess whitespace, and OCR artifacts."""
    if not text:
        return ""
    
    # Preserve page markers if present
    # Remove repetitive page numbers or header boilerplate like "Page 1 of 50"
    text = re.sub(r'(?i)Page\s+\d+\s+of\s+\d+', '', text)
    text = re.sub(r'(?i)CONFIDENTIAL\s+-\s+FOR\s+INTERNAL\s+USE\s+ONLY', '', text)
    
    # Clean up PDF bullet noise like "• • • • • • • 4"
    text = re.sub(r'(\s*•)+', ' ', text)
    
    # Remove standalone numeric lines (page number artifacts)
    lines = []
    for line in text.splitlines():
        line_s = re.sub(r'[ \t]+', ' ', line).strip()
        if line_s and not re.match(r'^\d+$', line_s):
            lines.append(line_s)
    
    cleaned = "\n".join(lines).strip()
    # Clean up multiple newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned

