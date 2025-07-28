# section_splitter.py
import re

def split_sections(document_name, pages):
    sections = []
    for page_number, text in enumerate(pages, start=1):
        lines = text.split('\n')
        current_section = ""
        current_title = None

        for line in lines:
            line_clean = line.strip()
            # Heading detection: line with all uppercase or starts with a number
            if re.match(r'^([A-Z][A-Z\s0-9\-:]{3,})$', line_clean) or re.match(r'^\d+[\.\)]?\s+[A-Z]', line_clean):
                if current_title and current_section:
                    sections.append({
                        "document": document_name,
                        "page": page_number,
                        "section_title": current_title,
                        "text": current_section.strip()
                    })
                current_title = line_clean
                current_section = ""
            else:
                current_section += line + " "

        # Add the last section
        if current_title and current_section:
            sections.append({
                "document": document_name,
                "page": page_number,
                "section_title": current_title,
                "text": current_section.strip()
            })
    return sections
