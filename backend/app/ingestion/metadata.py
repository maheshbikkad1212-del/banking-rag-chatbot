import re

def extract_document_metadata(doc_text: str, filename: str) -> dict:
    """Enriches chunk with document metadata: Name, Version, Effective Date, Authority, Category."""
    doc_id = "DOC-UNKNOWN"
    doc_name = filename
    authority = "General Banking Policy"
    effective_date = "2024-01-01"
    version = "1.0"
    category = "General Policy"

    # Extract Document ID
    doc_id_match = re.search(r'Document ID:\s*([^\n]+)', doc_text)
    if doc_id_match:
        doc_id = doc_id_match.group(1).strip()

    # Extract Document Name
    doc_name_match = re.search(r'Document Name:\s*([^\n]+)', doc_text)
    if doc_name_match:
        doc_name = doc_name_match.group(1).strip()

    # Extract Authority
    authority_match = re.search(r'Authority:\s*([^\n]+)', doc_text)
    if authority_match:
        authority = authority_match.group(1).strip()

    # Extract Effective Date
    date_match = re.search(r'Effective Date:\s*([^\n]+)', doc_text)
    if date_match:
        effective_date = date_match.group(1).strip()

    # Extract Version
    version_match = re.search(r'Version:\s*([^\n]+)', doc_text)
    if version_match:
        version = version_match.group(1).strip()

    # Extract Category
    category_match = re.search(r'Category:\s*([^\n]+)', doc_text)
    if category_match:
        category = category_match.group(1).strip()

    return {
        "doc_id": doc_id,
        "doc_name": doc_name,
        "authority": authority,
        "effective_date": effective_date,
        "version": version,
        "category": category,
        "source_filename": filename
    }
