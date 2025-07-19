import os
import json
from collections import defaultdict
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

def extract_font_styles(pdf_path):
    style_counts = defaultdict(int)

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        for char in text_line:
                            if isinstance(char, LTChar):
                                fontname = char.fontname
                                size = round(char.size, 1)
                                style = (fontname, size)
                                style_counts[style] += 1
    return style_counts

def extract_headings_and_title(pdf_path):
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
    from collections import defaultdict

    headings = []
    style_counts = defaultdict(int)
    line_data = []

    for page_layout in extract_pages(pdf_path):
        page_number = page_layout.pageid
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if not isinstance(text_line, LTTextLine):
                        continue

                    text = text_line.get_text().strip()
                    if not text:
                        continue

                    sizes = []
                    fonts = []

                    for char in text_line:
                        if isinstance(char, LTChar):
                            sizes.append(round(char.size, 1))
                            fonts.append(char.fontname)

                    if not sizes:
                        continue

                    avg_size = round(sum(sizes) / len(sizes), 1)
                    fontname = fonts[0] if fonts else ""
                    is_bold = "Bold" in fontname or "bold" in fontname

                    style_counts[(avg_size, is_bold)] += 1

                    line_data.append({
                        "text": text,
                        "size": avg_size,
                        "bold": is_bold,
                        "page": page_number
                    })

    # Rank styles: largest size + boldness + frequency
    sorted_styles = sorted(
        style_counts.items(),
        key=lambda x: (-x[0][0], -int(x[0][1]), -x[1])
    )

    # Pick top 3 heading styles
    heading_styles = [style for (style, _) in sorted_styles[:3]]

    outline = []
    for line in line_data:
        if (line["size"], line["bold"]) in heading_styles:
            if len(line["text"]) < 120:  # heuristics: headings are usually short
                outline.append({
                    "level": "H1",  # We'll improve level detection later
                    "text": line["text"],
                    "page": line["page"]
                })

    title = outline[0]["text"] if outline else ""
    return title, outline


def process_pdf(pdf_path, output_path):
    print(f"🔍 Processing {os.path.basename(pdf_path)}...")
    title, outline = extract_headings_and_title(pdf_path)
    data = {
        "title": title,
        "outline": outline
    }
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Processed {os.path.basename(pdf_path)} -> {os.path.basename(output_path)}")

def process_all_pdfs(input_dir, output_dir):
    print("🚀 Starting PDF outline extraction...")
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            input_pdf = os.path.join(input_dir, filename)
            output_json = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            process_pdf(input_pdf, output_json)
    print("✅ Completed.")

if __name__ == "__main__":
    process_all_pdfs("/app/input", "/app/output")
