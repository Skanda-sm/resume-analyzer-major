import os
import re
import json
import tempfile
from flask import Flask, request, render_template, redirect, url_for, flash
import pdfplumber
import docx
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK resources are available
for resource in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource)

# Load spaCy model safely
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "SpaCy model not found. Run: python -m spacy download en_core_web_sm"
    )

app = Flask(__name__)
app.secret_key = "dev-secret"  # change in production
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# Load skills list safely
SKILLS_FILE = "skills.json"
if not os.path.exists(SKILLS_FILE):
    raise FileNotFoundError(f"{SKILLS_FILE} not found. Please add your skills.json file.")

with open(SKILLS_FILE, "r", encoding="utf-8") as f:
    SKILLS_DB = [s.lower() for s in json.load(f)]

# Regex patterns
EMAIL_RE = re.compile(r"[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+")
PHONE_RE = re.compile(r"(\+?\d{1,3})?[\s\-\(]*\d{2,4}[\s\-\)]*\d{3,4}[\s\-]*\d{3,4}")

def extract_text_from_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            p = page.extract_text()
            if p:
                text.append(p)
    return "\n".join(text)

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(filepath, filename):
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    elif lower.endswith(".docx") or lower.endswith(".doc"):
        return extract_text_from_docx(filepath)
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def extract_contact_info(text):
    emails = EMAIL_RE.findall(text)
    phone_full = [m.group().strip() for m in re.finditer(PHONE_RE, text)]
    return {"emails": list(dict.fromkeys(emails)),
            "phones": list(dict.fromkeys(phone_full))}

def extract_name(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    head = "\n".join(lines[:30])
    doc = nlp(head)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            if len(name) < 100 and "@" not in name and any(c.isalpha() for c in name):
                return name
    if lines and len(lines[0].split()) <= 5:
        return lines[0]
    return None

def extract_education(text):
    edu_keywords = ["bachelor", "master", "b.sc", "b.tech", "m.tech", "m.sc", 
                    "phd", "diploma", "high school", "sslc", "hsc", "ug", "pg", "mba"]
    education = [s.strip() for s in sent_tokenize(text) if any(k in s.lower() for k in edu_keywords)]
    return list(dict.fromkeys(education))

def extract_experience(text):
    exp_keywords = ["experience", "worked", "intern", "project", 
                    "responsible", "achieved", "developed", "years"]
    exp_sents = [s.strip() for s in sent_tokenize(text) if any(k in s.lower() for k in exp_keywords)]
    return list(dict.fromkeys(exp_sents))[:20]

def extract_skills(text, top_n=30):
    text_low = text.lower()
    found = [skill for skill in SKILLS_DB if skill in text_low]
    return found[:top_n]

def score_against_job(resume_text, job_text):
    docs = [resume_text, job_text]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=2000)
    tfidf = vectorizer.fit_transform(docs)
    from sklearn.metrics.pairwise import linear_kernel
    sim = linear_kernel(tfidf[0:1], tfidf[1:2])[0][0]

    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))
    overlap = resume_skills & job_skills
    skill_score = len(overlap) / (len(job_skills) + 1e-6)

    final = 100 * (0.6 * sim + 0.4 * skill_score)
    return {
        "cosine_similarity": float(sim),
        "skill_overlap_count": len(overlap),
        "job_skills_count": len(job_skills),
        "skill_overlap": list(overlap),
        "final_score_percent": round(final, 2)
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded = request.files.get("resume")
        job_desc = request.form.get("job_desc", "").strip()
        if not uploaded:
            flash("Please upload a resume file (PDF or DOCX).")
            return redirect(url_for("index"))

        tmp = tempfile.NamedTemporaryFile(delete=False)
        uploaded.save(tmp.name)
        try:
            text = extract_text(tmp.name, uploaded.filename)
        finally:
            tmp.close()
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

        contact = extract_contact_info(text)
        name = extract_name(text)
        education = extract_education(text)
        experience = extract_experience(text)
        skills = extract_skills(text)

        job_score = score_against_job(text, job_desc) if job_desc else None

        result = {
            "name": name,
            "emails": contact.get("emails", []),
            "phones": contact.get("phones", []),
            "education": education,
            "experience": experience,
            "skills": skills,
            "job_score": job_score,
            "raw_text_snippet": "\n".join(text.splitlines()[:50])
        }
        return render_template("result.html", result=result, job_desc=job_desc)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
