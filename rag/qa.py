import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_JSON_DIR = os.path.join(BASE_DIR, "cleaned_json")
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def summarize_paper(paper):
    # build context from abstract + first 3 sections
    context = paper.get("abstract", "") + "\n\n"
    
    for section in paper.get("sections", [])[:3]:
        heading = section.get("heading", "")
        body = section.get("body", "")
        context += f"{heading}\n{body}\n\n"

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": "You are an expert ML researcher who explains research papers clearly to students learning machine learning."
            },
            {
                "role": "user",
                "content": f"""Read this ML research paper and summarize it in exactly this format:

**TL;DR:** (1-2 sentences, what this paper does in simple words)

**Problem:** (what problem does this paper solve?)

**Method:** (how did they solve it? what technique or model did they use?)

**Results:** (key numbers, accuracy, improvements they achieved)

**Why it matters:** (why should someone learning ML care about this?)

**3 things to remember:**
- 
- 
-

Paper content:
{context}"""
            }
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    os.makedirs(SUMMARIES_DIR, exist_ok=True)

    files = [f for f in os.listdir(CLEANED_JSON_DIR) if f.endswith(".json")]
    print(f"Found {len(files)} papers to summarize")

    for filename in files:
        paper_id = filename.replace(".json", "")
        print(f"\nSummarizing: {paper_id}")

        with open(os.path.join(CLEANED_JSON_DIR, filename), encoding="utf-8") as f:
            paper = json.load(f)

        summary = summarize_paper(paper)

        # save summary
        output_path = os.path.join(SUMMARIES_DIR, f"{paper_id}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Title: {paper['title']}\n\n")
            f.write(summary)

        print(summary[:300])
        print(f"Saved: {paper_id}.txt")

    print(f"\nDone! Summaries saved in: {SUMMARIES_DIR}")