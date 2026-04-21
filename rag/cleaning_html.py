import re
import os
import json
import sys
from bs4 import BeautifulSoup

# import your parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Scripts.paper_extractor import parse_paper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_HTML_DIR = os.path.join(BASE_DIR, "papers_html")
CLEANED_JSON_DIR = os.path.join(BASE_DIR, "cleaned_json")


# =========================
# CLEAN TEXT (SAFE)
# =========================
def clean_text(text):
    if not text:
        return ""

    # remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # normalize symbols
    text = text.replace("×", "x")
    text = text.replace("±", "+-")

    # remove citations [1], [2,3]
    text = re.sub(r'\[[0-9,\s]+\]', '', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =========================
# REMOVE INLINE MATH FROM TEXT
# =========================
def remove_inline_math(text):
    return re.sub(r'\$.*?\$', '', text)


# =========================
# EXTRACT MATH (NEW 🔥)
# =========================
def extract_math(soup):
    math_expressions = []

    for m in soup.find_all("math"):
        txt = m.get_text(" ", strip=True)
        if txt:
            math_expressions.append(txt)

    for m in soup.find_all(class_=re.compile("ltx_math")):
        txt = m.get_text(" ", strip=True)
        if txt:
            math_expressions.append(txt)

    return list(set(math_expressions))


# =========================
# CLEAN TABLES
# =========================
def clean_tables(tables):
    cleaned = []

    for table in tables:
        rows = []
        for row in table.get("rows", []):
            cleaned_row = [clean_text(cell) for cell in row if cell]
            if cleaned_row:
                rows.append(cleaned_row)

        cleaned.append({
            "caption": clean_text(table.get("caption", "")),
            "rows": rows
        })

    return cleaned


# =========================
# FILTER USELESS SECTIONS
# =========================
def is_useless_section(heading):
    heading = heading.lower()

    skip = [
        "acknowledgement",
        "acknowledgments",
        "bibliography",
        "funding"
    ]

    return any(k in heading for k in skip)


# =========================
# CLEAN FULL PAPER
# =========================
def clean_paper(html_content, paper_id):
    soup = BeautifulSoup(html_content, "html.parser")

    data = parse_paper(html_content, paper_id)

    cleaned_sections = []

    for sec in data.get("sections", []):
        heading = clean_text(sec.get("heading", ""))
        body = sec.get("body", "")

        body = remove_inline_math(body)
        body = clean_text(body)

        if not body:
            continue

        if is_useless_section(heading):
            continue

        cleaned_sections.append({
            "heading": heading,
            "body": body
        })

    return {
        "id": data.get("id", ""),
        "title": clean_text(data.get("title", "")),
        "authors": [clean_text(a) for a in data.get("authors", [])],
        "abstract": clean_text(data.get("abstract", "")),
        "sections": cleaned_sections,
        "figures": data.get("figures", []),
        "tables": clean_tables(data.get("tables", [])),
        "math": extract_math(soup)   # 🔥 NEW
    }


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    os.makedirs(CLEANED_JSON_DIR, exist_ok=True)

    files = os.listdir(PAPERS_HTML_DIR)
    html_files = [f for f in files if f.endswith(".html")]

    print(f"Found {len(html_files)} HTML files to clean")

    for filename in html_files:
        paper_id = filename.replace(".html", "")
        print(f"\nCleaning: {paper_id}")

        with open(os.path.join(PAPERS_HTML_DIR, filename), encoding="utf-8") as f:
            html_content = f.read()

        cleaned = clean_paper(html_content, paper_id)

        output_path = os.path.join(CLEANED_JSON_DIR, f"{paper_id}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)

        print(f"  Title: {cleaned['title'][:60]}")
        print(f"  Sections: {len(cleaned['sections'])}")
        print(f"  Tables: {len(cleaned['tables'])}")
        print(f"  Figures: {len(cleaned['figures'])}")
        print(f"  Math: {len(cleaned['math'])}")
        print(f"  Saved: {paper_id}.json")

    print(f"\nDone! Cleaned {len(html_files)} papers")
    print(f"Saved in: {CLEANED_JSON_DIR}")