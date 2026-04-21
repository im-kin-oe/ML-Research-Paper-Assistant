import os
import json
import re
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_HTML_DIR = os.path.join(BASE_DIR, "papers_html")
CLEANED_JSON_DIR = os.path.join(BASE_DIR, "cleaned_json")


# =========================
# RAW TEXT
# =========================
def extract_raw_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(" ", strip=True)


# =========================
# CLEANED TEXT
# =========================
def extract_cleaned_text(cleaned_json):
    texts = []

    texts.append(cleaned_json.get("title", ""))
    texts.append(cleaned_json.get("abstract", ""))

    for sec in cleaned_json.get("sections", []):
        texts.append(sec.get("heading", ""))
        texts.append(sec.get("body", ""))

    for table in cleaned_json.get("tables", []):
        texts.append(table.get("caption", ""))
        for row in table.get("rows", []):
            texts.extend(row)

    return " ".join(texts)


# =========================
# MATH EXTRACTION
# =========================
def extract_math_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    math_expressions = []

    for m in soup.find_all("math"):
        txt = m.get_text(" ", strip=True)
        if txt:
            math_expressions.append(txt)

    for m in soup.find_all(class_=re.compile("ltx_math")):
        txt = m.get_text(" ", strip=True)
        if txt:
            math_expressions.append(txt)

    return set(math_expressions)


# =========================
# COMPARE TEXT
# =========================
def compare_texts(raw, cleaned):
    raw_words = set(raw.lower().split())
    cleaned_words = set(cleaned.lower().split())

    missing = raw_words - cleaned_words

    # better filtering
    missing = [
        w for w in missing
        if len(w) > 4
        and not re.search(r'[\\\{\}]', w)
        and not w.isdigit()
        and not w.startswith("http")
    ]

    return missing[:30]


# =========================
# ELEMENT COUNTS
# =========================
def count_elements(html_content, cleaned_json):
    soup = BeautifulSoup(html_content, "html.parser")

    html_figs = len(soup.find_all("figure"))
    html_tables = len(soup.find_all("figure", class_=re.compile("ltx_table")))
    html_sections = len(soup.find_all(["section", "div"], class_=re.compile("ltx_(section|subsection)")))

    json_figs = len(cleaned_json.get("figures", []))
    json_tables = len(cleaned_json.get("tables", []))
    json_sections = len(cleaned_json.get("sections", []))

    return {
        "figures": (html_figs, json_figs),
        "tables": (html_tables, json_tables),
        "sections": (html_sections, json_sections)
    }


# =========================
# VALIDATE MATH
# =========================
def compare_math(html_content, cleaned_json):
    html_math = extract_math_from_html(html_content)
    json_math = set(cleaned_json.get("math", []))

    missing = html_math - json_math

    return list(missing)[:10]


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    files = [f for f in os.listdir(PAPERS_HTML_DIR) if f.endswith(".html")]

    for filename in files:
        paper_id = filename.replace(".html", "")
        print(f"\n🔍 Checking: {paper_id}")

        html_path = os.path.join(PAPERS_HTML_DIR, filename)
        json_path = os.path.join(CLEANED_JSON_DIR, f"{paper_id}.json")

        if not os.path.exists(json_path):
            print("❌ Missing cleaned JSON")
            continue

        with open(html_path, encoding="utf-8") as f:
            html_content = f.read()

        with open(json_path, encoding="utf-8") as f:
            cleaned_json = json.load(f)

        raw_text = extract_raw_text(html_content)
        cleaned_text = extract_cleaned_text(cleaned_json)

        # TEXT CHECK
        missing_words = compare_texts(raw_text, cleaned_text)

        # STRUCTURE CHECK
        counts = count_elements(html_content, cleaned_json)

        # MATH CHECK
        missing_math = compare_math(html_content, cleaned_json)

        print("📊 Element counts:")
        print(f"  Figures: HTML={counts['figures'][0]} | JSON={counts['figures'][1]}")
        print(f"  Tables : HTML={counts['tables'][0]} | JSON={counts['tables'][1]}")
        print(f"  Sections: HTML={counts['sections'][0]} | JSON={counts['sections'][1]}")

        print("\n⚠️ Missing words (sample):")
        print(missing_words)

        print("\n🧮 Missing math (sample):")
        print(missing_math)