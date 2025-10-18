from sentence_transformers import SentenceTransformer, util
import re

# Load lightweight embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


# -----------  Helper Functions  -----------

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{4}', text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().split("\n")
    for line in lines[:5]:  # look only in first few lines
        if len(line.split()) <= 5 and not re.search(r'\d', line):
            return line.strip().title()
    return None

def extract_skills(text):
    skillset = [
        "Python", "Java", "C++", "C#", "SQL", "NoSQL", "R", "Power BI", "Tableau",
        "HTML", "CSS", "JavaScript", "React", "Node.js", "Angular", "AWS",
        "Azure", "GCP", "Machine Learning", "Deep Learning", "AI", "NLP",
        "Docker", "Kubernetes", "Git", "Linux", "Excel", "Data Analysis"
    ]
    found = []
    for skill in skillset:
        if re.search(rf'\b{re.escape(skill)}\b', text, re.I):
            found.append(skill)
    return list(set(found))

def extract_education(text):
    education_keywords = ["B.Tech", "B.E", "Bachelor", "Master", "MBA", "M.Tech", "PhD", "BSc", "MSc"]
    matches = [edu for edu in education_keywords if re.search(rf"\b{edu}\b", text, re.I)]
    return matches

def extract_experience(text):
    exp = re.findall(r'(\d+)\+?\s*(?:year|yr|years|yrs)', text, re.I)
    if exp:
        years = max([int(e) for e in exp])
        return f"{years} years"
    return "Not specified"


# -----------  Main Function  -----------

def match_resume_to_job(resume_text, job_text, weights=None, mode="local", api_url=None):
    """
    Real AI-based resume-job matching + Info Extraction
    """
    if not resume_text.strip() or not job_text.strip():
        return {"score": 0, "parsed": {}, "error": "Empty text"}

    weights = weights or {"sim": 0.6, "skills": 0.3, "exp": 0.1}

    # Semantic similarity
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    job_emb = model.encode(job_text, convert_to_tensor=True)
    similarity = float(util.cos_sim(resume_emb, job_emb))

    # Skill overlap
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    overlap = len(set(resume_skills) & set(job_skills))
    total = len(set(job_skills)) or 1
    skill_score = overlap / total

    # Experience score
    exp_text = extract_experience(resume_text)
    exp_match = 0.1 if exp_text != "Not specified" else 0.05

    # Weighted score
    score = (similarity * weights["sim"]) + (skill_score * weights["skills"]) + (exp_match * weights["exp"])
    score = round(score, 2)

    # Extract personal info
    parsed = {
        "name": extract_name(resume_text),
        "email": extract_email(resume_text),
        "phone": extract_phone(resume_text),
        "skills": resume_skills,
        "education": extract_education(resume_text),
        "experience": exp_text,
        "semantic_similarity": round(similarity, 2),
        "skill_overlap": round(skill_score, 2),
        "experience_bonus": exp_match
    }

    return {"score": score, "parsed": parsed}
