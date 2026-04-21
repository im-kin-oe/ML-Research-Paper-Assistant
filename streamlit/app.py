import streamlit as st
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_JSON_DIR = os.path.join(BASE_DIR, "cleaned_json")
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")

st.set_page_config(page_title="ML Paper Assistant", layout="wide")
st.title("ML Paper Assistant")
st.subheader("Latest ML research — summarized daily")

with st.sidebar:
    st.title("⚙️ Settings")
    user_api_key = st.text_input(
        "Enter your Groq API key",
        type="password",
        placeholder="gsk_..."
    )
    st.markdown("[Get free Groq API key](https://console.groq.com)")
    
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. Enter your Groq API key")
    st.markdown("2. Browse summarized papers")
    st.markdown("3. Click Arxiv link to read full paper")


def load_papers():
    papers = []
    files = [f for f in os.listdir(CLEANED_JSON_DIR) if f.endswith(".json")]
    for filename in files:
        with open(os.path.join(CLEANED_JSON_DIR, filename), encoding="utf-8") as f:
            papers.append(json.load(f))
    return papers

def load_summary(paper_id):
    summary_path = os.path.join(SUMMARIES_DIR, f"{paper_id}.txt")
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            return f.read()
    return "Summary not available"

def show_paper_card(paper, summary):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(paper.get("title", "Untitled"))
        authors = paper.get("authors", [])
        if authors:
            st.write(f"**Authors:** {', '.join(authors[:3])}")
        st.write(f"**Sections:** {len(paper.get('sections', []))}")
        arxiv_id = paper.get("id", "")
        st.markdown(f"[📄 View on Arxiv](https://arxiv.org/abs/{arxiv_id})")

        figures = paper.get("figures", [])
        if figures:
            for fig in figures[:3]:
                img_src = fig.get("img_src")
                caption = fig.get("caption", "")
                if img_src:
                    try:
                        st.image(img_src, caption=caption[:100] if caption else "", use_container_width=600)
                    except:
                        pass
        else:
            st.info("No figures available")

    with col2:
        st.subheader("📝 Summary")
        st.markdown(summary)

papers = load_papers()

if not papers:
    st.error("No papers found. Run paper_extractor.py and summarizer.py first.")
else:
    st.success(f"Showing {len(papers)} papers")
    for paper in papers:
        summary = load_summary(paper["id"])
        show_paper_card(paper, summary)
        st.divider()