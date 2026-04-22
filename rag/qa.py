import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ FIX: use REAL structured data
CLEANED_JSON_DIR = os.path.join(BASE_DIR, "cleaned_json")

# ✅ output stays same
SUMMARIES_DIR = os.path.join(BASE_DIR, "streamlit", "summaries")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def summarize_paper(paper):
    # 🔥 better context (more useful info)
    context = f"Title: {paper.get('title','')}\n\n"
    context += f"Abstract:\n{paper.get('abstract','')}\n\n"

    # include more sections (not just 3 blindly)
    for section in paper.get("sections", [])[:5]:
        heading = section.get("heading", "")
        body = section.get("body", "")[:1000]  # avoid token overflow
        context += f"{heading}\n{body}\n\n"

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,  # more precise
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": """You are an expert ML researcher.
Explain papers clearly, accurately, and concisely.
Do NOT hallucinate missing details.
If results are missing, say "Not clearly stated"."""
            },
            {
                "role": "user",
                "content": f"""Summarize this ML research paper in this format:

**TL;DR:** (1-2 simple sentences)

**Problem:** (what problem is solved)

**Method:** (key idea, model, approach)

**Results:** (numbers, benchmarks, improvements — if not present say "Not clearly stated")

**Why it matters:** (practical importance)

**3 key takeaways:**
- 
- 
-

Paper:
{context}"""
            }
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    os.makedirs(SUMMARIES_DIR, exist_ok=True)

    # ✅ FIX: use JSON files
    files = [f for f in os.listdir(CLEANED_JSON_DIR) if f.endswith(".json")]
    print(f"Found {len(files)} papers to summarize")

    for filename in files:
        paper_id = filename.replace(".json", "")
        print(f"\nSummarizing: {paper_id}")

        # ✅ FIX: load REAL structured paper
        with open(os.path.join(CLEANED_JSON_DIR, filename), encoding="utf-8") as f:
            paper = json.load(f)

        summary = summarize_paper(paper)

        # save summary to streamlit folder
        output_path = os.path.join(SUMMARIES_DIR, f"{paper_id}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Title: {paper.get('title','')}\n\n")
            f.write(summary)

        print(summary[:300])
        print(f"Saved: {paper_id}.txt")

    print(f"\nDone! Summaries saved in: {SUMMARIES_DIR}")