# output_formatter.py
def build_output_json(documents, persona, job, ranked_sections, timestamp):
    extracted_sections = []
    subsection_analysis = []

    for section in ranked_sections:
        extracted_sections.append({
            "document": section["document"],
            "page": section["page"],
            "section_title": section["section_title"],
            "importance_rank": section["importance_rank"]
        })

        subsection_analysis.append({
            "document": section["document"],
            "refined_text": section["text"][:500],  # limit to first 500 chars
            "page": section["page"]
        })

    return {
        "metadata": {
            "documents": documents,
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": timestamp
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
