from sentence_transformers import SentenceTransformer, util
from pathlib import Path
from typing import List, Dict, Any

# IMPORTANT: Reuse your Round 1A logic and the detailed parser
from ..round1a.outline_extractor import extract_outline_from_pdf
from ..core.pdf_parser import extract_detailed_blocks

# --- Model Loading ---
MODEL_PATH = "models/sentence-transformer-model"
try:
    model = SentenceTransformer(MODEL_PATH)
    print("Sentence Transformer model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}. Make sure you have downloaded the model to '{MODEL_PATH}'.")
    model = None

# --- Configuration ---
# Control how many top sections to return in the final output
TOP_N_SECTIONS = 5 

def get_text_after_heading(heading_block: Dict[str, Any], all_blocks: List[Dict[str, Any]]) -> str:
    """
    Finds and returns the text content that directly follows a heading block.
    """
    content = []
    # Find all blocks on the same page that are positioned below the heading
    for block in all_blocks:
        if block['page'] == heading_block['page'] and block['bbox'][1] > heading_block['bbox'][3]:
            # Simple heuristic: assume text within a certain vertical distance is part of the section
            if block['bbox'][1] - heading_block['bbox'][3] < 50: # 50 pixels tolerance
                 content.append(block['text'])
    
    # Join the found text and limit its length for a concise summary
    full_text = " ".join(content)
    return (full_text[:400] + '...') if len(full_text) > 400 else full_text


def analyze_documents_for_persona(pdf_paths: List[Path], persona: str, job: str) -> Dict[str, Any]:
    """
    Analyzes documents to find the TOP N sections most relevant to a persona and job.
    """
    if model is None:
        raise RuntimeError("Sentence Transformer model is not available.")

    # --- Step 1: Create a query from the persona and job description ---
    query = f"As a {persona}, I need to {job}"
    query_embedding = model.encode(query, convert_to_tensor=True)

    # --- Step 2: Extract sections and create embeddings for all documents ---
    all_sections = []
    
    # We need all text blocks from all documents for the subsection analysis later
    all_docs_text_blocks = {}

    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            print(f"Warning: PDF file not found at {pdf_path}, skipping.")
            continue
        
        # Get all text blocks for subsection analysis
        detailed_blocks, _ = extract_detailed_blocks(str(pdf_path))
        all_docs_text_blocks[pdf_path.name] = detailed_blocks

        # Reuse your Round 1A outline extractor to find headings
        outline_data = extract_outline_from_pdf(str(pdf_path))
        
        # Find the full block info for each heading identified by the outline extractor
        for section_heading in outline_data.get("outline", []):
            for block in detailed_blocks:
                # Match the heading text and page to find the full block data
                if section_heading['text'] == block['text'] and section_heading['page'] == block['page']:
                    section_text = block["text"]
                    section_embedding = model.encode(section_text, convert_to_tensor=True)
                    similarity = util.cos_sim(query_embedding, section_embedding)
                    
                    # Store the full block info for later use
                    block['relevance_score'] = similarity.item()
                    block['document'] = pdf_path.name
                    all_sections.append(block)
                    break # Move to the next heading

    # --- Step 3: Rank sections and take the top N ---
    ranked_sections = sorted(all_sections, key=lambda x: x['relevance_score'], reverse=True)
    top_sections = ranked_sections[:TOP_N_SECTIONS]

    # --- Step 4: Perform subsection analysis ONLY for the top sections ---
    subsection_data = []
    for section in top_sections:
        # Get the full text content that follows the heading
        refined_text = get_text_after_heading(section, all_docs_text_blocks[section['document']])
        if refined_text: # Only add if we found some text
            subsection_data.append({
                "document": section["document"],
                "refined_text": refined_text,
                "page_number": section["page"]
            })

    # --- Step 5: Format the final output ---
    formatted_sections = [
        {
            "document": sec["document"],
            "section_title": sec["text"],
            "importance_rank": i + 1,
            "page_number": sec["page"]
        } for i, sec in enumerate(top_sections)
    ]
    
    return {
        "extracted_sections": formatted_sections,
        "subsection_analysis": subsection_data
    }