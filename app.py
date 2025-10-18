import streamlit as st
import pandas as pd
import time
from helpers import extract_text
from ai_integration import match_resume_to_job

st.set_page_config(page_title="Smart Recruitment Assistant", layout="wide")
st.title("🤖 Smart Recruitment Assistant")
st.caption("Powered by GenAI | Built for Hackathon Automation")

st.sidebar.header("⚙️ Configuration")
mode = st.sidebar.radio("Integration Mode", ["local (dummy)", "http (API)"])
if mode == "http (API)":
    api_url = st.sidebar.text_input("API URL", "http://localhost:5001/match")

st.markdown("""
### 🚀 Upload Resumes & Paste Job Description
This app compares resumes against your job description using AI similarity scoring.
""")

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF, DOCX, or TXT)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True
)

job_text = st.text_area("Paste Job Description Here", height=220, placeholder="e.g., React Developer with 2+ years experience, SQL, and API integration skills.")

col1, col2, col3 = st.columns(3)
with col1:
    w_sim = st.slider("Text Similarity Weight", 0.0, 1.0, 0.6)
with col2:
    w_skill = st.slider("Skill Overlap Weight", 0.0, 1.0, 0.3)
with col3:
    w_exp = st.slider("Experience Weight", 0.0, 1.0, 0.1)

run = st.button("🔍 Run Matching")

if run:
    if not uploaded_files:
        st.warning("Please upload at least one resume.")
        st.stop()
    if not job_text.strip():
        st.warning("Please paste a job description.")
        st.stop()

    weights = {"sim": w_sim, "skills": w_skill, "exp": w_exp}
    results = []

    progress = st.progress(0)
    status = st.empty()

    for i, file in enumerate(uploaded_files):
        status.text(f"Processing {file.name}...")
        resume_text = extract_text(file.name, file.read())
        try:
            if mode.startswith("http"):
                result = match_resume_to_job(resume_text, job_text, weights, mode="http", api_url=api_url)
            else:
                result = match_resume_to_job(resume_text, job_text, weights, mode="local")
        except Exception as e:
            result = {"error": str(e), "score": 0, "parsed": {}}

        result["filename"] = file.name
        results.append(result)
        progress.progress((i + 1) / len(uploaded_files))
        time.sleep(0.2)

    st.success("✅ Matching complete!")

    df = pd.DataFrame([{
        "Filename": r["filename"],
        "Score": round(r.get("score", 0), 2),
        "Error": r.get("error", ""),
        "Candidate Name": r.get("parsed", {}).get("name", "N/A")
    } for r in results])

    df = df.sort_values("Score", ascending=False)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Results CSV", csv, "results.csv", "text/csv")

    st.markdown("---")
    st.markdown("### 🔍 Candidate Details")
    for r in df.head(5).itertuples():
        item = next(x for x in results if x["filename"] == r.Filename)
        with st.expander(f"{r.Filename} — Score {r.Score}"):
            st.json(item.get("parsed", {}))
