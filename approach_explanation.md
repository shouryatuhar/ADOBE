Overview
Our system is a light weight, persona based document analysis tool that excavates and ranks the relevant content from a list of PDFs. The system is dynamic in nature and deals with different personas and job descriptions effectively using a combination of rule-based logic and semantic similarity, so generalization may happen across domains, like travel planning, HR onboarding, and recipe curation.

Methodology
1. Document Parsing and Structure Extraction
We utilize pdfminer.six for PDF parsing and the retrieval of text blocks along with their metadata, including page numbers and character-level styling information. Our parser also identifies heading hierarchies in terms of font size, bold, and position-based layouts. This allows us to break down the documents into logical sections and sub-sections.

2. Persona & Job Understanding
The input job-to-be-done and persona (challenge1b_input.json) are considered the "information need." We transform this into a search intent that drives our extraction step. This intent is compared against all the section headers and paragraphs of the PDF corpus.

3. Relevance Scoring and Ranking
In order to determine how well every section aligns with the task of the persona:

We calculate TF-IDF vectors of section headings and paragraphs.

We calculate a distinct TF-IDF vector for the persona + job prompt. 

Cosine similarity between the vectors produces a relevance score. 

Top 5 sections with the highest scores are chosen for inclusion in the extracted_sections list and ranked based on importance. Each section is also tagged with source document and page number. 

4. Subsection Refinement
For every chosen section, we return the most pertinent paragraphs or bullet points as refined_text in the subsection_analysis list. We maintain diversity in subtopics while retaining semantic consistency with the job-to-be-done.

Performance Constraints
Offline Execution: No use of internet. All model and logic run solely on CPU with no API calls.

Speed: Optimized to run under 60 seconds for a 3–5 document set in Python and scikit-learn.

Model Size: No big ML models are employed; we depend on quick, memory-friendly methods (TF-IDF and cosine similarity).

Language Agnostic: Our parser is capable of generalizing over English and other Unicode-supported scripts if fonts are extractable.

Extensibility
The system is extensible and can accommodate easy plug-in for embedding-based ranking (e.g., MiniLM or Sentence-BERT) if permitted in future rounds. It can also be extended to:

Visual layout analysis

Entity extraction

Timeline summarization