from sentence_transformers import SentenceTransformer, util
import re
import hashlib

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Cache dictionary
cache = {}

# ---------- Helper Functions ----------
def get_hash(resume_text, job_text):
    key = resume_text + job_text
    return hashlib.md5(key.encode('utf-8')).hexdigest()

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{4}', text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().split("\n")
    for line in lines[:5]:
        if len(line.split()) <= 5 and not re.search(r'\d', line):
            return line.strip().title()
    return None

def extract_skills(text):
    skillset = ["Python","Java","C++","SQL","R","React","Node.js","Machine Learning",
                "AI","AWS","HTML","CSS","JavaScript","Docker","Kubernetes","Git"]
    found = [s for s in skillset if re.search(rf'\b{re.escape(s)}\b', text, re.I)]
    return list(set(found))

def extract_education(text):
    degrees = ["B.Tech","B.E","Bachelor","Master","MBA","M.Tech","PhD","BSc","MSc"]
    return [d for d in degrees if re.search(rf"\b{d}\b", text, re.I)]

def extract_experience(text):
    exp = re.findall(r'(\d+)\+?\s*(?:year|yr|years|yrs)', text, re.I)
    return f"{max([int(e) for e in exp])} years" if exp else "Not specified"

# ---------- Main Function ----------
def match_resume_to_job(resume_text, job_text, weights=None, job_role=None):
    # Check cache first
    key = get_hash(resume_text, job_text)
    if key in cache:
        return cache[key]

    # Default weights
    role_weights = {
        "Software Developer": {"sim":0.2, "skills":0.7, "exp":0.1},
        "Data Analyst": {"sim":0.3, "skills":0.6, "exp":0.1},
        "ML Engineer": {"sim":0.5, "skills":0.4, "exp":0.1},
    }
    weights = weights or role_weights.get(job_role, {"sim":0.4, "skills":0.5, "exp":0.1})

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

    # Experience bonus
    exp_text = extract_experience(resume_text)
    exp_score = 0.1 if exp_text != "Not specified" else 0.05

    # Weighted score
    score = (similarity*weights["sim"]) + (skill_score*weights["skills"]) + (exp_score*weights["exp"])
    score = round(score,2)

    # Parse candidate info
    parsed = {
        "name": extract_name(resume_text),
        "email": extract_email(resume_text),
        "phone": extract_phone(resume_text),
        "skills": resume_skills,
        "education": extract_education(resume_text),
        "experience": exp_text,
        "semantic_similarity": round(similarity,2),
        "skill_overlap": round(skill_score,2),
        "experience_bonus": exp_score
    }

    result = {"score": score, "parsed": parsed}

    # Save to cache
    cache[key] = result
    return result
