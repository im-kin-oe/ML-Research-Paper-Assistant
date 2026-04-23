import streamlit as st
import os
import json

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ML Paper Assistant", layout="wide")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "cleaned_json")

st.title("📚 ML Research Paper Assistant")

# =========================
# LOAD PAPERS
# =========================
def load_papers():
    papers = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".json"):
            with open(os.path.join(DATA_DIR, file), encoding="utf-8") as f:
                data = json.load(f)
                papers.append(data)

    return papers


papers = load_papers()

if not papers:
    st.error("No papers found")
    st.stop()

# =========================
# SESSION STATE (selected paper)
# =========================
if "selected_paper" not in st.session_state:
    st.session_state.selected_paper = papers[0]

# =========================
# LAYOUT: 2 COLUMNS
# =========================
col1, col2 = st.columns([1, 2])

# =========================
# LEFT PANEL (paper list)
# =========================
with col1:
    st.subheader("📄 Papers")

    for paper in papers:
        if st.button(paper["title"], use_container_width=True):
            st.session_state.selected_paper = paper

# =========================
# RIGHT PANEL (content)
# =========================
with col2:
    paper = st.session_state.selected_paper

    st.header(paper.get("title", "No Title"))

    # Authors
    authors = ", ".join(paper.get("authors", []))
    st.markdown(f"**Authors:** {authors}")

    # Email (optional)
    if "emails" in paper:
        st.markdown(f"**Emails:** {', '.join(paper['emails'])}")

    st.markdown("---")

    # Summary
    st.subheader("📝 Summary")
    st.write(paper.get("summary", "No summary"))

    st.markdown("---")

    # Sections (collapsible)
    st.subheader("📖 Sections")

    for sec in paper.get("sections", [])[:5]:
        with st.expander(sec.get("heading", "Section")):
            st.write(sec.get("body", ""))

    st.markdown("---")

    # Figures
    st.subheader("🖼️ Figures")

    for fig in paper.get("figures", [])[:3]:
        if fig.get("img_src"):
            st.image(fig["img_src"])
            if fig.get("caption"):
                st.caption(fig["caption"])