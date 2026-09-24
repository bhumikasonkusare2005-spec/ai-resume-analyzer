"""Flask entry point for the AI Resume Analyzer."""

from __future__ import annotations

import os
from io import BytesIO

from flask import Flask, flash, redirect, render_template, request, url_for
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

from analyzer import analyze_resume


app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,
    SECRET_KEY=os.environ.get("SESSION_SECRET", "resume-analyzer-local-secret"),
)

ALLOWED_EXTENSIONS = {"pdf"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _extract_pdf_text(file_storage) -> str:
    reader = PdfReader(BytesIO(file_storage.read()))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n".join(page for page in pages if page)


@app.errorhandler(413)
def file_too_large(_error):
    flash("That PDF is larger than 10 MB. Please upload a smaller file.", "error")
    return redirect(url_for("index"))


@app.get("/")
def index():
    return render_template("index.html", analysis=None, form_data={"job_description": ""})


@app.post("/analyze")
def analyze():
    resume = request.files.get("resume")
    job_description = request.form.get("job_description", "").strip()

    if not resume or not resume.filename:
        flash("Upload a PDF resume to get started.", "error")
        return render_template("index.html", analysis=None, form_data={"job_description": job_description}), 400
    if not _allowed_file(resume.filename) or not secure_filename(resume.filename):
        flash("Please upload a valid PDF file.", "error")
        return render_template("index.html", analysis=None, form_data={"job_description": job_description}), 400
    if len(job_description) < 40:
        flash("Add a little more detail to the job description so the match is meaningful.", "error")
        return render_template("index.html", analysis=None, form_data={"job_description": job_description}), 400

    try:
        resume_text = _extract_pdf_text(resume)
    except Exception:
        flash("We couldn't read that PDF. Try exporting the resume again as a text-based PDF.", "error")
        return render_template("index.html", analysis=None, form_data={"job_description": job_description}), 400

    if len(resume_text.strip()) < 40:
        flash("This PDF does not contain enough selectable text to analyze. Try a text-based PDF instead of a scan.", "error")
        return render_template("index.html", analysis=None, form_data={"job_description": job_description}), 400

    analysis = analyze_resume(resume_text, job_description)
    analysis["filename"] = secure_filename(resume.filename)
    return render_template(
        "index.html",
        analysis=analysis,
        form_data={"job_description": job_description},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("NODE_ENV") == "development")