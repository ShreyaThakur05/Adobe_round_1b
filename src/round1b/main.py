import json
from pathlib import Path
from datetime import datetime, timezone

from ..schemas.output_schemas import Round1BInput, Round1BOutput
from .relevance_analyzer import analyze_documents_for_persona

def run_round1b(input_dir_path: Path, output_dir_path: Path, models_dir_path: Path):
    """
    Main function to execute the Round 1B processing logic for a single collection.
    """
    # 1. Define file paths
    input_json_path = input_dir_path / "challenge1b_input.json"
    output_json_path = output_dir_path / "challenge1b_output.json"
    pdfs_dir_path = input_dir_path / "PDFs"

    print(f"Starting Round 1B processing for {input_json_path}")

    # 2. Read and parse the input JSON using the Pydantic schema
    if not input_json_path.exists():
        raise FileNotFoundError(f"Input JSON not found at {input_json_path}")
        
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    input_data = Round1BInput(**data)

    # 3. Get the full path for each PDF document
    pdf_file_paths = [pdfs_dir_path / doc.filename for doc in input_data.documents]

    # 4. Call your core analysis function
    analysis_result = analyze_documents_for_persona(
        pdf_paths=pdf_file_paths,
        persona=input_data.persona.role,
        job=input_data.job_to_be_done.task
    )
    
    # 5. Structure the final output
    final_output_data = {
        "metadata": {
            "input_documents": [doc.filename for doc in input_data.documents],
            "persona": input_data.persona.role,
            "job_to_be_done": input_data.job_to_be_done.task,
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        },
        "extracted_sections": analysis_result.get("extracted_sections", []),
        "subsection_analysis": analysis_result.get("subsection_analysis", [])
    }

    # 6. Validate and write the output JSON
    validated_output = Round1BOutput(**final_output_data)
    with open(output_json_path, "w", encoding='utf-8') as f:
        f.write(validated_output.model_dump_json(indent=4))
    
    print(f"Successfully created Round 1B output at {output_json_path}")

def run():
    """
    This is the entry point for the Docker container. It processes the
    single collection mounted by the 'docker run' command.
    """
    # These paths are the ones inside the Docker container
    INPUT_DIR = Path("/app/input")
    OUTPUT_DIR = Path("/app/output")
    MODELS_DIR = Path("/app/models")
    
    # Ensure the output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        run_round1b(INPUT_DIR, OUTPUT_DIR, MODELS_DIR)
    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == '__main__':
    run()