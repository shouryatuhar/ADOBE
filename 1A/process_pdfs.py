import os
import json
import re
import unicodedata
from collections import Counter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

HEADING_KEYWORDS = {
    "mission statement", "goals", "pathway options",
    "regular pathway", "distinction pathway",
    "elective course offerings", "what colleges say!"
}

def clean_heading(text):
    text = text.replace('\u00a0', ' ')
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\x20-\x7E\u00A0-\u024F]+', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def normalize_for_match(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKD', s.lower()).replace('\u00a0', ' ').strip())

def extract_font_styles(pdf_path):
    font_stats = Counter()
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_fonts = set()
                    try:
                        for char in text_line:
                            if isinstance(char, LTChar):
                                line_fonts.add((char.fontname, round(char.size, 1)))
                    except TypeError:
                        continue
                    for font in line_fonts:
                        font_stats[font] += 1
    return font_stats

def extract_headings_and_title(pdf_path):
    font_stats = extract_font_styles(pdf_path)

    def is_numeric(val):
        try: float(val); return True
        except: return False

    sorted_styles = sorted(
        [(style, count) for style, count in font_stats.items() if is_numeric(style[1])],
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
                    raw_text = line.get_text().strip()
                    if not raw_text or len(raw_text) > 300:
                        continue
                    if re.fullmatch(r'[\s\d\.\-•·‣•‧●○□…‥]+', raw_text):
                        continue
                    if 'table of contents' in raw_text.lower():
                        continue

                    try:
                        line_fonts = [(char.fontname, round(char.size, 1)) for char in line if isinstance(char, LTChar)]
                    except TypeError:
                        continue

                    if not line_fonts:
                        continue

                    sizes = [fs for _, fs in line_fonts]
                    most_common_size = Counter(sizes).most_common(1)[0][0]
                    font_names = [fn for fn, _ in line_fonts]
                    is_bold = any("Bold" in fn or "bold" in fn for fn in font_names)

                    cleaned = clean_heading(raw_text)
                    norm_line = normalize_for_match(cleaned)
                    if not cleaned or len(re.findall(r'[A-Za-z]', cleaned)) < 3:
                        continue

                    matched_keywords = [kw for kw in HEADING_KEYWORDS if kw in norm_line]
                    score = 3 if matched_keywords else (2 if is_bold else 1)

                    if most_common_size >= size_thresholds["H1"]:
                        level = "H1"
                    elif most_common_size >= size_thresholds["H2"]:
                        level = "H2"
                    elif most_common_size >= size_thresholds["H3"]:
                        level = "H3"
                    else:
                        continue

                    if score >= 2:
                        headings.append({
                            "level": level,
                            "text": cleaned,
                            "page": page_number
                        })

                        if not title_candidate and page_number == 1 and level == "H1":
                            title_candidate = cleaned

    return title_candidate or (headings[0]["text"] if headings else ""), headings

def process_pdf(pdf_path, output_path):
    title, outline = extract_headings_and_title(pdf_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"title": title, "outline": outline}, f, indent=2, ensure_ascii=False)

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
