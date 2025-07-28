# pdf_reader.py
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def extract_text_by_page(pdf_path):
    pages = []
    for page_layout in extract_pages(pdf_path):
        page_text = ""
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                page_text += element.get_text()
        pages.append(page_text.strip())
    return pages
