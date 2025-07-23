import os
import json
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from collections import defaultdict, Counter

import re
import unicodedata

def clean_heading(text):
    # Replace non-breaking spaces and control characters
    text = text.replace('\u00a0', ' ').replace('\xa0', ' ')
    text = unicodedata.normalize('NFKD', text)

    # Remove non-ASCII characters except basic punctuation
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Strip leading/trailing spaces and normalize whitespace
    return re.sub(r'\s+', ' ', text).strip()

# Define heading keywords to boost
HEADING_KEYWORDS = {
    "mission statement", "goals", "pathway options",
    "regular pathway", "distinction pathway",
    "elective course offerings", "what colleges say!"
}

def extract_font_styles(pdf_path):
    font_stats = Counter()
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_fonts = set()
                    for char in text_line:
                        if isinstance(char, LTChar):
                            font_key = (char.fontname, round(char.size, 1))
                            line_fonts.add(font_key)
                    for font in line_fonts:
                        font_stats[font] += 1
    return font_stats

def extract_headings_and_title(pdf_path):
    style_counts = extract_font_styles(pdf_path)

    def is_numeric(value):
        try:
            float(value)
            return True
        except:
            return False

    sorted_styles = sorted(
        [(style, count) for style, count in style_counts.items() if is_numeric(style[1])],
        key=lambda x: (-x[1], -float(x[0][1]))
    )
    font_size_order = [float(style[0][1]) for style in sorted_styles]
    if not font_size_order:
        font_size_order = [12, 11, 10]

    size_thresholds = {
        "H1": font_size_order[0],
        "H2": font_size_order[1] if len(font_size_order) > 1 else font_size_order[0] - 1,
        "H3": font_size_order[2] if len(font_size_order) > 2 else font_size_order[-1] - 1
    }

    headings = []
    title_candidate = None

    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=1):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for line in element:
                    line_text = line.get_text().strip()
                    if not line_text or len(line_text) > 300:
                        continue

                    line_fonts = []
                    for char in line:
                        if isinstance(char, LTChar):
                            line_fonts.append((char.fontname, round(char.size, 1)))

                    if not line_fonts:
                        continue

                    sizes = [fs for _, fs in line_fonts]
                    most_common_size = Counter(sizes).most_common(1)[0][0]
                    font_names = [fn for fn, _ in line_fonts]
                    is_bold = any("Bold" in fn or "bold" in fn for fn in font_names)

                    line_text_clean = ' '.join(line_text.split())
                    line_text_lower = line_text_clean.lower()

                    matched_keywords = [kw for kw in HEADING_KEYWORDS if kw in line_text_lower]

                    if matched_keywords and len(matched_keywords) > 1:
                        for kw in matched_keywords:
                            headings.append({
                                "level": "H3",
                                "text": kw.title(),
                                "page": page_number
                            })
                        continue

                    if matched_keywords:
                        score = 3
                    elif is_bold:
                        score = 2
                    else:
                        score = 1

                    if most_common_size >= size_thresholds["H1"]:
                        level = "H1"
                    elif most_common_size >= size_thresholds["H2"]:
                        level = "H2"
                    elif most_common_size >= size_thresholds["H3"]:
                        level = "H3"
                    else:
                        continue

if score >= 2:
    cleaned_text = clean_heading(line_text_clean)

    # Filter out lines that are just dots, dashes, or digits
    if not cleaned_text or re.fullmatch(r'[\d\s\.\-]+', cleaned_text):
        continue

    headings.append({
        "level": level,
        "text": cleaned_text,
        "page": page_number
    })

                        

if not title_candidate and page_number == 1 and score >= 2 and level == "H1":
                        title_candidate = line_text_clean

    return title_candidate or (headings[0]["text"] if headings else ""), headings


def process_pdf(pdf_path, output_path):
    title, outline = extract_headings_and_title(pdf_path)
    result = {
        "title": title,
        "outline": outline
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def process_all_pdfs(input_dir, output_dir):
    print("Starting PDF outline extraction...")
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            input_pdf = os.path.join(input_dir, file)
            output_json = os.path.join(output_dir, file.replace(".pdf", ".json"))
            print(f"Processing {file}...")
            try:
                process_pdf(input_pdf, output_json)
                print(f" Saved to {output_json}")
            except Exception as e:
                print(f" Failed to process {file}: {e}")

if __name__ == "__main__":
    process_all_pdfs("/app/input", "/app/output")
