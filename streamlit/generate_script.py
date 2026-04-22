import os
import json
from groq import Groq
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env file")
    exit()

client = Groq(api_key=api_key)

# =========================
# PATH SETUP
# =========================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "cleaned_json")

print("📂 Using data folder:", DATA_DIR)

if not os.path.exists(DATA_DIR):
    print("❌ ERROR: cleaned_json folder not found")
    exit()

# =========================
# SUMMARY FUNCTION
# =========================
def summarize_paper(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an ML expert. Summarize this research paper in clear bullet points."
                },
                {
                    "role": "user",
                    "content": text[:4000]
                }
            ],
            temperature=0.3,
            max_tokens=800
        )

        return response.choices[0].message.content

    except Exception as e:
        print("❌ API Error:", e)
        return None


# =========================
# MAIN PROCESS
# =========================
files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

if not files:
    print("⚠️ No JSON files found in cleaned_json/")
    exit()

for file in files:
    path = os.path.join(DATA_DIR, file)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Skip if already summarized
    if data.get("summary"):
        print(f"⏩ Skipping {file} (already has summary)")
        continue

    print(f"🧠 Summarizing {file}...")

    # Build input text
    text = data.get("abstract", "")

    for sec in data.get("sections", [])[:2]:
        text += "\n" + sec.get("body", "")

    if not text.strip():
        print(f"⚠️ No usable text in {file}")
        continue

    summary = summarize_paper(text)

    if not summary:
        print(f"❌ Failed to summarize {file}")
        continue

    # Save summary
    data["summary"] = summary

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved summary for {file}")

print("\n🎉 DONE: All papers processed!")