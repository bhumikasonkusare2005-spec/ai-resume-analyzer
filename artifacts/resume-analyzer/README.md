# AI Resume Analyzer

A small Flask web application that helps job seekers tailor a resume to a role. Upload a text-based PDF resume, paste a job description, and get an explainable match report.

## What it does

- Extracts selectable text from PDF resumes with `PyPDF2`
- Identifies skills from a curated vocabulary with common aliases
- Compares resume and job description text with TF-IDF vectors and cosine similarity
- Combines semantic similarity with detected skill overlap into a 0–100 match score
- Shows matching skills, missing or unstated skills, keywords to consider, and practical improvement suggestions
- Processes files in memory; it does not save uploaded resumes

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`.

The Replit preview workflow runs `pnpm --filter @workspace/resume-analyzer run dev`, which starts the Flask server using the injected `PORT`.

## Project structure

```text
app.py          Flask routes, PDF upload validation, and page rendering
analyzer.py     Skill extraction, TF-IDF scoring, and suggestion logic
templates/      Jinja page for the input and results states
static/         Responsive styles and small client-side enhancements
requirements.txt Python runtime dependencies
```

## Notes

Scanned/image-only PDFs do not contain selectable text and cannot be analyzed by `PyPDF2`. Export the resume as a text-based PDF before uploading.