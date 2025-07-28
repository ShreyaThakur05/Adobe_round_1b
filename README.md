# 🧠 Persona-Based Insight Engine – Adobe Hackathon Round 1B

A semantic document analysis system that identifies the **most relevant sections and summaries** from multiple PDFs, tailored to a specific persona and their job-to-be-done.

Built for **offline**, **CPU-only**, and **containerized** environments – fully compliant with Adobe Hackathon 2025 constraints.

---

## 📂 Project Structure

```bash
.
├── input/
│   ├── challenge1b_input.json       # Defines persona, job-to-be-done, and PDFs
│   └── PDFs/                        # Folder with input PDFs
│       ├── file1.pdf
│       ├── file2.pdf
│       └── ...
├── output/
│   └── round1b/
│       └── challenge1b_output.json # Final output JSON
├── models/
│   └── sentence-transformer-model/ # Pre-downloaded SBERT model
├── src/
│   ├── core/
│   │   └── pdf_parser.py           # Extracts low-level text blocks
│   ├── round1b/
│   │   ├── main.py                 # Entrypoint script
│   │   └── relevance_analyzer.py  # Document analysis and ranking logic
│   ├── schemas/
│   │   └── output_schemas.py       # Pydantic schema validation
├── requirements.txt
├── Dockerfile
└── README.md  (this file)

```
---
## 🚀 Features

- 🤖 **Understands user intent** from persona and job-to-be-done  
- 🔍 **Ranks top 5 relevant sections** using Sentence-BERT embeddings  
- 🧠 **Performs sub-section summarization** below matched headings  
- 🧩 **Modular, scalable, and fully offline architecture**

## 🧰 Libraries & Tools Used

| Library              | Purpose                          |
|----------------------|----------------------------------|
| `sentence-transformers` | Semantic similarity scoring      |
| `PyMuPDF (fitz)`         | PDF parsing and text layout     |
| `Pydantic`               | Input/output schema validation  |
| `torch`, `numpy`         | Embedding + similarity backend  |
| `json`, `os`, `re`       | General purpose utilities       |

