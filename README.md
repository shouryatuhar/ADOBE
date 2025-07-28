# Round 1B — Persona-Driven Document Intelligence

This solution extracts and prioritizes the most relevant document sections based on a given persona and their job-to-be-done.

## 🧪 How to Run

```bash
docker build -t persona-doc-analyzer .
docker run --rm -v "$PWD:/app" persona-doc-analyzer python process_collection.py "Collection 1"

