import os
import json
from collections import defaultdict, Counter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

# Known heading keywords to boost signal
KEYWORDS = [
    "mission statement", "goals", "pathway options",
    "regular pathway", "distinction pathway", "elective course offerings", "what colleges say"
]

def extract_font_styles(pdf_path):
    style_counts = Counter()
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        for char in text_line:
                            if isinstance(char, LTChar):
                                fontname = char.fontname
                                size = round(char.size, 1)
                                style_counts[(fontname, size)] += 1
    return style_counts

def is_bold(fontname):
    return "Bold" in fontname or "bold" in fontname

def extract_headings_and_title(pdf_path):
    style_counts = extract_font_styles(pdf_path)
    sorted_styles = sorted(style_counts.items(), key=lambda x: (-x[1], -x[0][1] if isinstance(x[0][1], (int, float)) else 0))
    if not sorted_styles:
        return "", []

    dominant_fonts = [item[0] for item in sorted_styles[:5]]  # Top 5 fonts

    headings = []
    title = ""
    seen_titles = set()

    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=1):
        lines = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for line in element:
                    if isinstance(line, LTTextLine):
                        line_text = line.get_text().strip()
                        if not line_text or line_text.lower() in seen_titles:
                            continue

                        fontnames = set()
                        sizes = []

                        for char in line:
                            if isinstance(char, LTChar):
                                fontnames.add(char.fontname)
                                sizes.append(char.size)

                        if not sizes:
                            continue
                        avg_size = sum(sizes) / len(sizes)
                        is_bold_line = any(is_bold(fn) for fn in fontnames)

                        style_key = next(((fn, round(avg_size, 1)) for fn in fontnames if (fn, round(avg_size, 1)) in dominant_fonts), None)

                        if style_key and (is_bold_line or style_key in dominant_fonts or any(kw in line_text.lower() for kw in KEYWORDS)):
                            level = "H1" if avg_size >= 13 else "H2" if avg_size >= 11 else "H3"
                            headings.append({"text": line_text, "page": page_num, "level": level})
                            seen_titles.add(line_text.lower())

    if headings:
        title = headings[0]["text"]
    return title, headings

def process_pdf(input_pdf, output_json):
    title, outline = extract_headings_and_title(input_pdf)
    output_data = {"title": title, "outline": outline}
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

def process_all_pdfs(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print("🚀 Starting PDF outline extraction...")
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            json_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            print(f"🔍 Processing {filename}...")
            process_pdf(pdf_path, json_path)
    print("✅ Completed.")
