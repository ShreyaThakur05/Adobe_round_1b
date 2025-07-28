import re
from ..core.pdf_parser import extract_detailed_blocks

def extract_semantic_info_from_pdf(pdf_path: str) -> dict:
    blocks, _ = extract_detailed_blocks(pdf_path)
    if not blocks:
        return {"title": None, "fields": {}, "keywords": []}

    texts = [b["text"].strip() for b in blocks if b["text"].strip()]
    full_text = "\n".join(texts)

    fields = {}

    # --- Title: largest bold on page 1 ---
    first_page_blocks = [b for b in blocks if b["page"] == 1 and b["bold"]]
    title = None
    if first_page_blocks:
        max_size = max(b["size"] for b in first_page_blocks)
        large_title_lines = [b["text"] for b in first_page_blocks if b["size"] == max_size]
        if len(large_title_lines) <= 5:
            title = " ".join(large_title_lines).strip()
    if not title and texts:
        title = texts[0]

    # --- Regex-based field detection ---
    field_patterns = {
        "address": r"\d{3,5}[^\n]{0,50}(PIGEON FORGE|TN|NY|CA|ADDRESS)[^\n]*",
        "rsvp": r"rsvp[:\s]+[^\n]+",
        "date": r"\b(?:\d{1,2}[/-]){2}\d{2,4}\b|\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{1,2},?\s+\d{4}",
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "phone": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "website": r"https?://[^\s]+|www\.[^\s]+|topjump\.com",
    }

    for key, pattern in field_patterns.items():
        match = re.findall(pattern, full_text, re.IGNORECASE)
        if match:
            fields[key] = list(set(match))

    # --- Keyword Collection ---
    raw_keywords = set()
    for line in texts:
        line_l = line.lower()
        if any(k in line_l for k in ["location", "venue", "party", "meeting", "invitation", "form", "instructions", "rsvp", "waiver", "guardians", "shoes", "topjump"]):
            raw_keywords.update(re.findall(r"\b\w{3,}\b", line_l))  # collect meaningful words only

    # --- Stopword Filtering ---
    stopwords = {"the", "and", "you", "are", "not", "that", "for", "with", "this", "from", "have", "will", "your", "please", "can", "but", "was", "any"}
    keywords = [w for w in raw_keywords if w not in stopwords]

    return {
        "title": title,
        "fields": fields,
        "keywords": sorted(keywords)
    }
