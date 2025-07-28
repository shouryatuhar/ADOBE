# Adobe-India-Hackathon25
This repository contains my complete solutions for both rounds of the Adobe India Hackathon 2025:

- **Round 1A:** Heading Detection from PDFs
- **Round 1B:** Persona-Driven Document Intelligence

Each round is self-contained, Dockerized, and runs completely offline on CPU within the provided constraints.

---

##  Round 1A — PDF Heading Structure Extraction

> **Goal:** Extract a structured outline (Title, H1, H2, H3 with page numbers) from a PDF document.

###  Features:
- Merges multi-line bold headings
- Uses font size, weight, and position for level inference
- Keyword-based soft boosting (e.g., "Mission Statement", "Goals", etc.)
- Filters out TOC/footers/page numbers
- Output format: Clean, hierarchical JSON with depth levels

### Run Instructions:
cd 1A
docker build -t adobe-hackathon:supermin .
docker run --rm -v "$PWD/input:/app/input" -v "$PWD/output:/app/output" adobe-hackathon:supermin

## Round 1B — Persona-Driven Document Intelligence
> **Goal:** Extract and prioritize the most relevant sections from a collection of PDFs, tailored to a specific persona and job-to-be-done.

## **Features**:
Supports diverse domains (travel, cooking, software tutorials)

Analyzes each document and ranks important sections

Provides refined sub-section summaries

CPU-only, under 1GB RAM, offline processing under 60 seconds

Output in the exact required JSON format

**Run Instructions**:

docker build -t persona-doc-analyzer .
docker run --rm -v "$PWD:/app" persona-doc-analyzer python process_collection.py "Collection 1"
docker run --rm -v "$PWD:/app" persona-doc-analyzer python process_collection.py "Collection 2"
docker run --rm -v "$PWD:/app" persona-doc-analyzer python process_collection.py "Collection 3"
**Output**:
Saved to Collection X/challenge1b_output.json

