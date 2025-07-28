import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple

def extract_detailed_blocks(pdf_path: str) -> Tuple[List[Dict[str, Any]], List[Tuple[float, float]]]:
    """
    Extracts detailed text blocks with metadata from each page of a PDF.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A tuple containing:
        - A list of dictionaries, where each dictionary represents a text span
          and contains its text, size, font, boldness, and coordinates.
        - A list of page dimensions (width, height) for each page.
    """
    doc = fitz.open(pdf_path)
    blocks = []
    page_dimensions = []
    
    for page_num, page in enumerate(doc, start=1):
        page_dimensions.append((page.rect.width, page.rect.height))
        page_blocks = page.get_text("dict")["blocks"]
        for block in page_blocks:
            if block["type"] == 0:  # 0 indicates a text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Check the font flags for boldness
                        is_bold = span["flags"] & 2**4
                        
                        blocks.append({
                            "text": span["text"].strip(),
                            "size": round(span["size"]),
                            "font": span["font"],
                            "bold": bool(is_bold),
                            "bbox": span["bbox"], # (x0, y0, x1, y1)
                            "page": page_num,
                        })
    return blocks, page_dimensions