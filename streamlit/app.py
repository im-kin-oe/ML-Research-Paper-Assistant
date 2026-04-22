import streamlit as st
import os
import json

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ML Paper Assistant", layout="wide")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "cleaned_json")

# =========================
# UI HEADER
# =========================
st.title("ML Paper Assistant")
st.subheader("Latest ML research — summarized daily")

# =========================
# SIDEBAR
# =========================
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
    st.markdown("1. Browse papers")
    st.markdown("2. Read summary")
    st.markdown("3. Explore sections & figures")


# =========================
# LOAD PAPERS
# =========================
def load_papers():
    papers = []

    if not os.path.exists(DATA_DIR):
        st.error(f"❌ Folder not found: {DATA_DIR}")
        st.stop()

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

    if not files:
        st.warning("⚠️ No JSON files found in cleaned_json/")
        return papers

    for filename in files:
        path = os.path.join(DATA_DIR, filename)

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            papers.append({
                "id": data.get("id"),
                "title": data.get("title"),
                "abstract": data.get("abstract", ""),
                "summary": data.get("summary", "No summary yet"),
                "sections": data.get("sections", []),
                "figures": data.get("figures", [])
            })

        except Exception as e:
            st.warning(f"Error reading {filename}: {e}")

    return papers


# =========================
# SHOW PAPER CARD
# =========================
def show_paper_card(paper):
    col1, col2 = st.columns([1, 2])

    # LEFT SIDE
    with col1:
        title = paper.get("title") or paper.get("id", "Untitled")
        st.subheader(title)

        arxiv_id = paper.get("id", "")
        if arxiv_id:
            st.markdown(f"[📄 View on Arxiv](https://arxiv.org/abs/{arxiv_id})")

        st.markdown(f"**Sections:** {len(paper.get('sections', []))}")

    # RIGHT SIDE
    with col2:
        st.subheader("📝 Summary")

        summary = paper.get("summary", "")
        if summary:
            st.markdown(summary)
        else:
            st.info("No summary available yet")

    # =========================
    # SECTIONS
    # =========================
    sections = paper.get("sections", [])
    if sections:
        st.subheader("📖 Key Sections")

        for sec in sections[:3]:  # limit to 3
            heading = sec.get("heading", "Section")
            body = sec.get("body", "")

            with st.expander(heading):
                st.write(body[:1000])  # limit text

    # =========================
    # FIGURES
    # =========================
    figures = paper.get("figures", [])
    if figures:
        st.subheader("📷 Figures")

        for fig in figures[:2]:  # limit images
            img = fig.get("img_src")
            caption = fig.get("caption", "")

            if img:
                st.image(img, use_container_width=True)
                if caption:
                    st.caption(caption)


# =========================
# MAIN
# =========================
papers = load_papers()

if not papers:
    st.error("No papers found. Make sure cleaned_json/ exists and has data.")
else:
    st.success(f"Showing {len(papers)} papers")

    for paper in papers:
        show_paper_card(paper)
        st.divider()