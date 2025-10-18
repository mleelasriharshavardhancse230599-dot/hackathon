# app.py

import streamlit as st
import pandas as pd
from helpers import extract_text
from ai_integration import match_resume_to_job
from database import save_result_to_db, get_past_results

# --- Streamlit Page Config ---
st.set_page_config(page_title="Smart Recruitment Assistant", layout="wide")
st.title("🤖 Smart Recruitment Assistant")

# --- Job Role Selection (Dynamic Mapping) ---
job_role = st.selectbox(
    "Select Job Role",
    ["Software Developer", "Data Analyst", "ML Engineer"]
)

# --- Job Description Input ---
job_description = st.text_area(
    "Paste Job Description",
    height=200
)

# --- Resume Upload ---
uploaded_files = st.file_uploader(
    "Upload Resumes (PDF, DOCX, TXT)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True
)

# --- Run Matching ---
run = st.button("Run Matching")

if run:
    if not uploaded_files or not job_description.strip():
        st.warning("Please upload resumes and enter a job description.")
        st.stop()

    results = []

    for file in uploaded_files:
        # Extract text from resume
        text = extract_text(file.name, file.read())

        # Match resume with job description (AI + dynamic weights + caching)
        res = match_resume_to_job(text, job_description, job_role=job_role)

        # Save result to database
        save_result_to_db(file.name, job_role, res)

        # Append for display
        results.append({"filename": file.name, **res})

    # --- Convert results to DataFrame for display ---
    df = pd.DataFrame([{
        "Filename": r["filename"],
        "Score": r["score"],
        "Name": r["parsed"]["name"],
        "Email": r["parsed"]["email"],
        "Phone": r["parsed"]["phone"],
        "Skills": ", ".join(r["parsed"]["skills"]),
        "Education": ", ".join(r["parsed"]["education"]),
        "Experience": r["parsed"]["experience"]
    } for r in results])

    # Sort by score descending
    df = df.sort_values("Score", ascending=False)

    # Display table
    st.subheader("Ranked Candidate List")
    st.dataframe(df, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "results.csv")

# --- Optional: Show past results for same role ---
if st.checkbox("Show Past Results for This Role"):
    past = get_past_results(job_role)
    if past:
        past_df = pd.DataFrame([{
            "Filename": r["filename"],
            "Score": r["score"],
            "Name": r["name"],
            "Email": r["email"],
            "Phone": r["phone"],
            "Skills": ", ".join(r["skills"]),
            "Education": ", ".join(r["education"]),
            "Experience": r["experience"]
        } for r in past])
        past_df = past_df.sort_values("Score", ascending=False)
        st.subheader("Past Candidates")
        st.dataframe(past_df, use_container_width=True)
    else:
        st.info("No past results found for this role.")
