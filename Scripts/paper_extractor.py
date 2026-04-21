import requests
from bs4 import BeautifulSoup
import os
import re
import time
import json

ARXIV_URL = "https://arxiv.org/list/cs.LG/recent?skip=760&show=50"

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
PAPERS_HTML_DIR = os.path.join(BASE_DIR, "papers_html")
PAPERS_JSON = os.path.join(BASE_DIR, "papers.json")


# =========================
# FETCHING
# =========================
def fetch_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text


def get_paper_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    papers = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("/abs/"):
            paper_id = href.replace("/abs/", "")
            papers.append({
                "id": paper_id,
                "abs_url": f"https://arxiv.org{href}",
                "html_url": f"https://arxiv.org/html/{paper_id}"
            })

    seen = set()
    unique = []
    for p in papers:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)

    return unique[:10]


def fetch_paper_html(paper):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(paper["html_url"], headers=headers)
    return response.text


# =========================
# EXTRACTION HELPERS
# =========================

def extract_sections(soup):
    sections = []

    for section in soup.find_all(["section", "div"], class_=re.compile("ltx_(section|subsection)")):

        heading_tag = section.find(["h2", "h3"], class_=re.compile("ltx_title"))
        if not heading_tag:
            continue

        heading = heading_tag.get_text(" ", strip=True)

        texts = []

        # ✅ robust extraction (handles different structures)
        for element in section.find_all(["p", "li"]):
            txt = element.get_text(" ", strip=True)
            if txt:
                texts.append(txt)

        body = " ".join(texts)

        if body:
            sections.append({
                "heading": heading,
                "body": body
            })

    return sections


def extract_figures(soup):
    figures = []

    for fig in soup.find_all("figure"):

        # image (if exists)
        img = fig.find("img")
        img_src = None

        if img:
            src = img.get("src")
            if src:
                if not src.startswith("http"):
                    src = f"https://arxiv.org/html/{src}"
                img_src = src

        # caption
        caption_tag = fig.find("figcaption")
        caption = caption_tag.get_text(" ", strip=True) if caption_tag else ""

        figures.append({
            "img_src": img_src,
            "caption": caption
        })

    return figures

def extract_tables(soup):
    tables = []

    for fig in soup.find_all("figure", class_=re.compile("ltx_table")):
        table = fig.find("table")
        if not table:
            continue

        rows = []
        for tr in table.find_all("tr"):
            cols = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
            if cols:
                rows.append(cols)

        caption_tag = fig.find("figcaption")
        caption = caption_tag.get_text(" ", strip=True) if caption_tag else ""

        tables.append({
            "caption": caption,
            "rows": rows
        })

    return tables


# =========================
# MAIN PARSER
# =========================

def parse_paper(html_content, paper_id):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Title
    title_tag = soup.find("h1", class_=re.compile("ltx_title"))
    title = title_tag.get_text(" ", strip=True) if title_tag else "No title"

    # Authors
    authors = []
    for author in soup.find_all(class_=re.compile("ltx_personname")):
        txt = author.get_text(" ", strip=True)
        if txt:
            authors.append(txt)

    # Abstract
    abstract_tag = soup.find(class_=re.compile("ltx_abstract"))
    abstract = abstract_tag.get_text(" ", strip=True) if abstract_tag else "No abstract"

    # Sections
    sections = extract_sections(soup)

    # Figures
    figures = extract_figures(soup)

    # Tables
    tables = extract_tables(soup)

    return {
        "id": paper_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "sections": sections,
        "figures": figures,
        "tables": tables
    }


# =========================
# MAIN EXECUTION
# =========================

if __name__ == "__main__":
    print(f"Saving to: {BASE_DIR}")
    print("Fetching paper list...")

    html = fetch_page(ARXIV_URL)
    papers = get_paper_links(html)

    print(f"Found {len(papers)} papers")

    all_papers = []
    os.makedirs(PAPERS_HTML_DIR, exist_ok=True)

    for i, paper in enumerate(papers):
        print(f"\nFetching paper {i+1}: {paper['id']}")

        paper_html = fetch_paper_html(paper)

        if "No HTML" in paper_html or len(paper_html) < 500:
            print("  Skipping — no HTML version")
            continue

        # save raw HTML
        fixed_html = paper_html.replace('src="', 'src="https://arxiv.org/html/')
        with open(os.path.join(PAPERS_HTML_DIR, f"{paper['id']}.html"), "w", encoding="utf-8") as f:
            f.write(fixed_html)

        parsed = parse_paper(paper_html, paper["id"])
        all_papers.append(parsed)

        print(f"  Title: {parsed['title'][:60]}")
        print(f"  Sections: {len(parsed['sections'])}")
        print(f"  Figures: {len(parsed['figures'])}")
        print(f"  Tables: {len(parsed['tables'])}")

        time.sleep(1)

    if not all_papers:
        print("No papers fetched — all were PDF only")
    else:
        with open(PAPERS_JSON, "w", encoding="utf-8") as f:
            json.dump(all_papers, f, ensure_ascii=False, indent=2)

        print(f"\nDone! Fetched {len(all_papers)} papers")
        print(f"HTML saved in: {PAPERS_HTML_DIR}")
        print(f"JSON saved in: {PAPERS_JSON}")

        print(f"\nFirst paper: {all_papers[0]['title']}")
        print(f"Sections: {len(all_papers[0]['sections'])}")
        print(f"Tables: {len(all_papers[0]['tables'])}")