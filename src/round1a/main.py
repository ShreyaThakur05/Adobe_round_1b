import json
from pathlib import Path
from ..schemas.output_schemas import Round1AOutput
from .outline_extractor import extract_outline_from_pdf
from .semantic_extractor import extract_semantic_info_from_pdf
from pydantic import ValidationError

def process_round1a_files(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Processing files from: {input_path.resolve()}")
    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found to process.")
        return

    for pdf_file in pdf_files:
        print(f"--- Processing {pdf_file.name} ---")

        # Step 1: Extract outline
        raw_outline = extract_outline_from_pdf(str(pdf_file))

        # Step 2: Fix poor title using semantic extractor
        semantic_info = extract_semantic_info_from_pdf(str(pdf_file))
        final_title = raw_outline.get("title", "Untitled Document")
        if final_title.strip().lower() in {"untitled", "untitled document"} or len(final_title.strip()) < 5:
            final_title = semantic_info.get("title") or final_title

        # Step 3: Enforce max 10 outline items
        trimmed_outline = raw_outline.get("outline", [])

        # Step 4: Prepare final JSON structure
        raw_output_data = {
            "title": final_title,
            "outline": trimmed_outline
        }

        try:
            # Validate using Pydantic schema
            validated_output = Round1AOutput(**raw_output_data)
            print("Validation successful.")

            # Save the output
            output_json_path = output_path / f"{pdf_file.stem}.json"
            with open(output_json_path, "w", encoding="utf-8") as f:
                f.write(validated_output.model_dump_json(indent=4))
            print(f"Successfully created output: {output_json_path.name}")

        except ValidationError as e:
            print(f"!!! VALIDATION FAILED for {pdf_file.name} !!!")
            print(e)

        print("-" * (len(pdf_file.name) + 20))

def run():
    INPUT_DIR = "input/round1a"
    OUTPUT_DIR = "output/round1a"
    process_round1a_files(INPUT_DIR, OUTPUT_DIR)

if __name__ == "__main__":
    run()
# import json
# from pathlib import Path
# from ..schemas.output_schemas import Round1AOutput
# from .outline_extractor import extract_outline_from_pdf
# from pydantic import ValidationError

# def process_round1a_files(input_dir: str, output_dir: str):
#     """
#     Processes all PDFs in the input directory for Round 1A, validates the
#     extracted outline, and saves it as a JSON file.
#     """
#     input_path = Path(input_dir)
#     output_path = Path(output_dir)
#     output_path.mkdir(parents=True, exist_ok=True)

#     print(f"Processing files from: {input_path.resolve()}")
#     pdf_files = list(input_path.glob("*.pdf"))
    
#     if not pdf_files:
#         print("No PDF files found to process.")
#         return

#     for pdf_file in pdf_files:
#         print(f"--- Processing {pdf_file.name} ---")
        
#         raw_output_data = extract_outline_from_pdf(str(pdf_file))

#         try:
#             validated_output = Round1AOutput(**raw_output_data)
#             print("Validation successful.")

#             output_json_path = output_path / f"{pdf_file.stem}.json"
#             with open(output_json_path, "w", encoding="utf-8") as f:
#                 f.write(validated_output.model_dump_json(indent=4))
#             print(f"Successfully created output: {output_json_path.name}")

#         except ValidationError as e:
#             print(f"!!! VALIDATION FAILED for {pdf_file.name} !!!")
#             print(e)
        
#         print("-" * (len(pdf_file.name) + 20))


# def run():
#     # These paths are placeholders for local testing.
#     # The Docker container will use /app/input and /app/output.
#     INPUT_DIR = "input/round1a"
#     OUTPUT_DIR = "output/round1a"
#     process_round1a_files(INPUT_DIR, OUTPUT_DIR)


# if __name__ == "__main__":
#     run()