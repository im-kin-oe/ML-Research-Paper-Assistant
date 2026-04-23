# Chunking From Pdf 
import os
import fitz # PyMuPDF

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
PAPERS_PDF_PATH = os.path.join(BASE_DIR, "papers_pdf")

def extract_pages(PAPER_PDF_PATH):
    doc = fitz.open(PAPER_PDF_PATH)
    pages = []


    for i , page in enumerate(doc):
        text = page.get_text()
        pages.append({
                "page_num": i + 1,
                "text":text
            })
    
    return pages 


pages = extract_pages(PAPERS_PDF_PATH)


