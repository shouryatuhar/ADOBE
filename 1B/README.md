README for Round 1A: PDF Heading Structure Extraction
# Adobe India Hackathon 2025 - Round 1A
## Problem Statement
Extract a structured outline (Title, H1, H2, H3 with page numbers) from a PDF document in a clean
JSON format.
---
## Features
- Merges multi-line bold headings into one
- Uses font size, boldness, and vertical position to determine heading levels
- Soft-boosts keywords like "Mission Statement", "Goals", etc.
- Eliminates TOC, footers, and false headings like page numbers
- Supports multilingual PDFs
- Completely offline, runs on CPU-only
---
## Run Instructions
```bash
cd 1A
# Build Docker image
docker build -t adobe-hackathon:supermin .
# Run the solution
# (Assumes PDFs are in ./input and output will be stored in ./output)
docker run --rm -v "$PWD/input:/app/input" -v "$PWD/output:/app/output"
adobe-hackathon:supermin
```
Output will be saved in `output/<filename>.json`
---
## Constraints Met
- CPU only
- Model size under 200MB
- Finishes within 10s for 50-page PDFs
- Offline / no internet
---
## Folder Structure
1A/
??? input/ # PDFs to process
??? output/ # Extracted heading JSONs
??? heading_extraction.py # Core logic
??? Dockerfile