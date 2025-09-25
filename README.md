AI Resume Analyzer – Project Description

The AI Resume Analyzer is an intelligent application designed to automatically extract, analyze, and evaluate information from resumes.
It leverages Natural Language Processing (NLP) and Machine Learning (ML) techniques to make the recruitment process faster, more accurate, and more efficient.

🔧 Key Features

Resume Parsing

Extracts text from PDF, DOC, and DOCX files.

Identifies key sections like Name, Contact Info, Education, Work Experience, and Skills.

Skill Extraction & Matching

Matches candidate skills against a predefined skill database.

Highlights both exact and related matches.

Job Description Comparison

Allows recruiters to paste a job description.

Uses TF-IDF similarity and skill overlap analysis to score how well the resume matches the role.

Contact Information Detection

Extracts phone numbers and email IDs using regex patterns.

Smart Name Detection

Uses spaCy Named Entity Recognition (NER) to identify the candidate’s name.

Education & Experience Extraction

Identifies degrees, certifications, and professional experience.

Scoring & Recommendations

Generates a final compatibility score (0–100%) between the resume and the job description.

Provides insights on missing or weak areas in the resume.

⚙️ Tech Stack

Frontend: HTML, CSS, Flask templates

Backend: Python, Flask

Libraries:

pdfplumber & python-docx → Extract text from resumes

spaCy → Named Entity Recognition (NER) for names and entities

NLTK → Sentence tokenization and text preprocessing

scikit-learn (TF-IDF, cosine similarity) → Resume–Job description matching

Storage: JSON file for predefined skills database

🎯 Benefits

Saves recruiters significant time by automating resume screening.

Ensures unbiased and consistent evaluation of candidates.

Helps candidates understand their strengths and gaps with respect to a job posting.

The page will run on http://127.0.0.1:5000/ here.
