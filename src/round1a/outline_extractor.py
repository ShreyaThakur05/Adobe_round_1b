import re
import statistics
from collections import defaultdict
from ..core.pdf_parser import extract_detailed_blocks

def extract_outline_from_pdf(pdf_path: str) -> dict:
    """
    Extracts a clean and accurate outline by passing text blocks through a
    multi-stage filtering pipeline before classifying them as headings based on
    structure (numbering) and style (font properties).
    """
    text_blocks, page_dims = extract_detailed_blocks(pdf_path)
    if not text_blocks:
        return {"title": "Empty Document", "outline": []}

    # --- 1. Title Extraction ---
    title = "Untitled Document"
    # A title is usually the largest, bold text on the first page.
    page1_blocks = [b for b in text_blocks if b['page'] == 1 and b['bold']]
    if page1_blocks:
        max_size = max(b['size'] for b in page1_blocks)
        title = " ".join([b['text'] for b in page1_blocks if b['size'] == max_size]).strip()

    # --- 2. Font Analysis ---
    # Use median for a more robust measure of the document's body font size
    font_sizes = [b['size'] for b in text_blocks]
    median_size = statistics.median(font_sizes) if font_sizes else 12

    # --- 3. Multi-Stage Filtering and Candidate Collection ---
    candidates = []
    # This regex specifically targets the noisy revision history table rows
    revision_table_pattern = re.compile(r"^\d\.\d\s+\d{1,2}\s+[A-Z]{3,}\s+\d{4}")

    for block in text_blocks:
        # --- FILTERING PIPELINE ---
        # Filter 1: Skip if it's a long sentence or too short to be a heading
        if len(block['text'].split()) > 15 or len(block['text'].strip()) < 5:
            continue
        if not any(c.isalpha() for c in block['text']):
            continue
        # Filter 2: Skip if it looks like a page footer
        if "page" in block['text'].lower() and "of" in block['text'].lower():
            continue
        # Filter 3: THE KEY FIX - Skip if it matches a known table row pattern
        if revision_table_pattern.match(block['text']):
            continue
            
        # --- If it survives filtering, add it as a candidate ---
        candidates.append(block)

    # --- 4. Final Classification ---
    outline = []
    # heading_pattern = re.compile(r"^\s*(\d+(\.\d+))\.?\s+(.)")
    heading_pattern = re.compile(r"^\s*(\d+(\.\d+))\.?\s+(.)") 

    # Group candidates by style (font size and boldness)
    styled_headings = defaultdict(list)
    numbered_headings = []

    for cand in candidates:
        match = heading_pattern.match(cand['text'])
        if match:
            # It's a structural heading, classify by number
            numbering, text = match.group(1), match.group(2).strip()
            level = f"H{min(numbering.count('.') + 1,3)}"
            # numbered_headings.append({"level": level, "text": text, "page": cand['page']})
            numbered_headings.append({"level": level, "text": f"{numbering} {text}", "page": cand['page']})
        # elif cand['size'] > median_size and cand['bold']:
        elif cand['size'] > median_size * 1.15 or (cand['bold'] and cand['size'] >= median_size):
            # It's a stylistic heading, group it for later classification
            # style_key = (cand['size'], cand['bold'])
            style_key = (round(cand['size'], 2), cand['bold'])
            styled_headings[style_key].append(cand)
    
    # Classify the stylistic headings based on their font size hierarchy
    sorted_styles = sorted(styled_headings.keys(), key=lambda x: x[0], reverse=True)
    style_to_level = {style: f"H{min(i + 1, 3)}" for i, style in enumerate(sorted_styles) }

    for style, blocks in styled_headings.items():
        if style in style_to_level:
            level = style_to_level[style]
            for block in blocks:
                # Ensure the title is not added to the outline
                if block['text'] != title:
                    outline.append({"level": level, "text": block['text'], "page": block['page']})

    # Combine, sort, and deduplicate
    outline.extend(numbered_headings)
    outline.sort(key=lambda x: x['page'])

    final_outline = []
    seen = set()
    for item in outline:
        if item['text'] not in seen:
            final_outline.append(item)
            seen.add(item['text'])

    return {"title": title, "outline": final_outline}



# import re
# import statistics
# from collections import defaultdict
# from ..core.pdf_parser import extract_detailed_blocks

# def extract_outline_from_pdf(pdf_path: str) -> dict:
#     """
#     Extracts a highly accurate outline using a feature-based classification
#     engine to analyze the style, content, and context of every text block.
#     """
#     all_spans, page_dims = extract_detailed_blocks(pdf_path)
#     if not all_spans:
#         return {"title": "Empty Document", "outline": []}

#     # --- 1. Line Reconstruction & Global Font Analysis ---
#     lines = []
#     # Group spans into visually distinct lines based on page and vertical position
#     for page_num in range(1, len(page_dims) + 1):
#         page_spans = sorted([s for s in all_spans if s['page'] == page_num], key=lambda s: (s['bbox'][1], s['bbox'][0]))
#         if not page_spans: continue
        
#         current_line_spans = [page_spans[0]]
#         for i in range(1, len(page_spans)):
#             # If vertical distance is small, it's the same line
#             if abs(page_spans[i]['bbox'][1] - current_line_spans[-1]['bbox'][1]) < 5:
#                 current_line_spans.append(page_spans[i])
#             else:
#                 lines.append(current_line_spans)
#                 current_line_spans = [page_spans[i]]
#         lines.append(current_line_spans)
        
#     font_sizes = [s['size'] for s in all_spans if s['text'].strip()]
#     median_size = statistics.median(font_sizes) if font_sizes else 12

#     # --- 2. Feature Engineering & Candidate Selection ---
#     candidates = []
#     heading_pattern = re.compile(r"^\s*(\d+(\.\d+)|Appendix\s+[A-Z])\.?\s+(.)")

#     for i, line_spans in enumerate(lines):
#         line_text = " ".join(s['text'] for s in line_spans if s['text']).strip()
#         if not line_text: continue
        
#         features = {
#             "text": line_text,
#             "size": line_spans[0]['size'],
#             "bold": all(s['bold'] for s in line_spans),
#             "page": line_spans[0]['page'],
#             "word_count": len(line_text.split()),
#             "space_above": lines[i][0]['bbox'][1] - lines[i-1][-1]['bbox'][3] if i > 0 and lines[i][0]['page'] == lines[i-1][0]['page'] else 30,
#             "starts_with_number": heading_pattern.match(line_text),
#             "is_all_caps": line_text.isupper() and len(line_text) > 4
#         }

#         # --- High-Precision Classification Rules ---
#         is_heading = False
#         # Rule 1: Numbered headings are the most reliable signal.
#         if features['starts_with_number'] and features['word_count'] < 12:
#             is_heading = True
#         # Rule 2: Un-numbered headings must have strong contextual and style signals.
#         elif features['word_count'] < 10 and not line_text.endswith(('.', ':', ',')):
#             # Must have significant empty space above it AND be bold.
#             if features['space_above'] > (features['size'] * 0.7) and features['bold']:
#                 is_heading = True
#             # OR be very large and bold (for main titles/headings).
#             elif features['size'] > median_size * 1.5 and features['bold']:
#                 is_heading = True
#             # OR be all caps and have significant space above (for flyers).
#             elif features['is_all_caps'] and features['space_above'] > 15:
#                 is_heading = True
        
#         if is_heading:
#             candidates.append(features)

#     if not candidates:
#         return {"title": "Untitled Document", "outline": []}

#     # --- 3. Title Extraction & Final Classification ---
#     page1_candidates = [c for c in candidates if c['page'] == 1]
#     title_block = max(page1_candidates, key=lambda x: x['size']) if page1_candidates else candidates[0]
#     title = title_block['text']
    
#     outline = []
#     numbered_headings = [c for c in candidates if c['starts_with_number']]
#     styled_headings = [c for c in candidates if not c['starts_with_number'] and c != title_block]
    
#     for h in numbered_headings:
#         match = h['starts_with_number']
#         text = match.group(3) if match.group(3) else h['text']
#         numbering = match.group(1)
#         # Handle both numbered and Appendix style headings
#         level = f"H{numbering.count('.') + 1}" if '.' in numbering or numbering.isdigit() else "H1"
#         outline.append({"level": level, "text": text.strip(), "page": h['page']})

#     if styled_headings:
#         unique_sizes = sorted(list(set(h['size'] for h in styled_headings)), reverse=True)
#         size_to_level = {size: f"H{i+1}" for i, size in enumerate(unique_sizes) if i < 3}
#         for h in styled_headings:
#             level = size_to_level.get(h['size'])
#             if level:
#                 outline.append({"level": level, "text": h['text'], "page": h['page']})

#     # --- 4. Final Assembly ---
#     outline.sort(key=lambda x: x['page'])
#     final_outline = []
#     seen = set()
#     for item in outline:
#         if item['text'] and item['text'] not in seen:
#             final_outline.append(item)
#             seen.add(item['text'])

#     return {"title": title, "outline": final_outline}