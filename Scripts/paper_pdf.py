import requests
from bs4 import BeautifulSoup
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
PAPERS_DIR = os.path.join(BASE_DIR, "papers")  # ✅ saves in project folder

url = "https://arxiv.org/list/cs.LG/recent?skip=760&show=50"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
papers = soup.find_all("dt")

os.makedirs(PAPERS_DIR, exist_ok=True)

for i, paper in enumerate(papers[:10]):
    link_tag = paper.find("a", title="Abstract")
    if link_tag:
        abs_link = "https://arxiv.org" + link_tag.get("href")
        pdf_link = abs_link.replace("/abs/", "/pdf/") + ".pdf"
        filename = os.path.join(PAPERS_DIR, f"paper_{i+1}.pdf")  # ✅
        print(f"Downloading: {pdf_link}")
        try:
            r = requests.get(pdf_link, headers={"User-Agent": "Mozilla/5.0"})
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Error: {e}")

print("Done!")