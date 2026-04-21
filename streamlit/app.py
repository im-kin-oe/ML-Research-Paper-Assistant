import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SUMMARIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summaries")

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


# ✅ FIX: load summaries instead of JSON papers
def load_papers():
    papers = []
    files = [f for f in os.listdir(SUMMARIES_DIR) if f.endswith(".txt")]

    for filename in files:
        paper_id = filename.replace(".txt", "")
        path = os.path.join(SUMMARIES_DIR, filename)

        with open(path, encoding="utf-8") as f:
            content = f.read()

        papers.append({
            "id": paper_id,
            "title": paper_id,
            "summary": content
        })

    return papers


# ❌ removed old load_summary (not needed anymore)


def show_paper_card(paper):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(paper.get("title", "Untitled"))
        arxiv_id = paper.get("id", "")
        st.markdown(f"[📄 View on Arxiv](https://arxiv.org/abs/{arxiv_id})")

    with col2:
        st.subheader("📝 Summary")
        st.markdown(paper.get("summary", "No summary"))


papers = load_papers()

if not papers:
    st.error("No summaries found. Make sure .txt files exist in streamlit/summaries/")
else:
    st.success(f"Showing {len(papers)} papers")
    for paper in papers:
        show_paper_card(paper)
        st.divider()