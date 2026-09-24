"""Resume/job description analysis helpers.

The analyzer intentionally stays explainable: the score comes from TF-IDF
similarity, while skills are matched from a curated, editable vocabulary.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "JavaScript": ("javascript", "js", "ecmascript"),
    "TypeScript": ("typescript", "ts"),
    "Java": ("java",),
    "C++": ("c++", "cpp"),
    "C#": ("c#", "c sharp"),
    "Go": ("golang", "go"),
    "Ruby": ("ruby",),
    "PHP": ("php",),
    "SQL": ("sql",),
    "PostgreSQL": ("postgresql", "postgres"),
    "MySQL": ("mysql",),
    "MongoDB": ("mongodb", "mongo"),
    "Redis": ("redis",),
    "React": ("react", "react.js", "reactjs"),
    "Next.js": ("next.js", "nextjs", "next js"),
    "Angular": ("angular",),
    "Vue": ("vue", "vue.js", "vuejs"),
    "Node.js": ("node.js", "nodejs", "node js"),
    "Django": ("django",),
    "Flask": ("flask",),
    "FastAPI": ("fastapi",),
    "REST APIs": ("rest api", "restful api", "rest apis"),
    "GraphQL": ("graphql",),
    "HTML": ("html",),
    "CSS": ("css",),
    "Tailwind CSS": ("tailwind", "tailwind css"),
    "Git": ("git", "github", "gitlab"),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure",),
    "GCP": ("gcp", "google cloud", "google cloud platform"),
    "Terraform": ("terraform",),
    "CI/CD": ("ci/cd", "continuous integration", "continuous delivery"),
    "Linux": ("linux",),
    "Machine Learning": ("machine learning", "ml"),
    "Natural Language Processing": ("natural language processing", "nlp"),
    "Data Analysis": ("data analysis", "data analytics"),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "scikit-learn": ("scikit-learn", "sklearn"),
    "TensorFlow": ("tensorflow",),
    "PyTorch": ("pytorch",),
    "Tableau": ("tableau",),
    "Power BI": ("power bi",),
    "Figma": ("figma",),
    "Agile": ("agile",),
    "Scrum": ("scrum",),
    "Jira": ("jira",),
    "Project Management": ("project management",),
    "Communication": ("communication", "communicator"),
    "Leadership": ("leadership", "leader"),
    "Problem Solving": ("problem solving", "problem-solving"),
}

ACTION_VERBS = {
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "drove",
    "generated",
    "improved",
    "launched",
    "led",
    "managed",
    "optimized",
    "reduced",
    "automated",
    "increased",
    "implemented",
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_term(text: str, term: str) -> bool:
    escaped = re.escape(term.lower()).replace(r"\ ", r"\s+")
    if term.lower() in {"c++", "c#", "c sharp", "c++"}:
        return re.search(escaped, text, flags=re.IGNORECASE) is not None
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text, flags=re.IGNORECASE) is not None


def extract_skills(text: str) -> set[str]:
    normalised = _normalise(text)
    return {
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if any(_contains_term(normalised, alias) for alias in aliases)
    }


def _term_frequency(text: str, terms: Iterable[str]) -> Counter[str]:
    tokens = re.findall(r"[a-z][a-z0-9+#.-]{1,}", _normalise(text))
    counts = Counter(tokens)
    return Counter({term: counts[term.lower()] for term in terms})


def _top_keywords(job_description: str, resume_text: str, limit: int = 8) -> list[str]:
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=80)
    matrix = vectorizer.fit_transform([job_description, resume_text])
    job_weights = matrix[0].toarray().ravel()
    resume_weights = matrix[1].toarray().ravel()
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(
        (
            (float(weight), term)
            for weight, term, resume_weight in zip(job_weights, terms, resume_weights)
            if weight > 0 and resume_weight == 0
        ),
        reverse=True,
    )
    return [term for _, term in ranked[:limit]]


def make_suggestions(
    resume_text: str,
    job_description: str,
    matching_skills: list[str],
    missing_skills: list[str],
    score: int,
) -> list[dict[str, str]]:
    suggestions: list[dict[str, str]] = []
    resume_lower = _normalise(resume_text)
    job_lower = _normalise(job_description)

    if missing_skills:
        preview = ", ".join(missing_skills[:3])
        suffix = " and other skills" if len(missing_skills) > 3 else ""
        suggestions.append({
            "title": "Address the highest-priority gaps",
            "body": f"If you have relevant experience, add evidence for {preview}{suffix}. Mirror the job description's wording naturally.",
        })

    quantified = bool(re.search(r"\b\d+%|\b\d+\+|\$\d+|\b\d+\s*(?:users|customers|projects|hours|people)\b", resume_lower))
    if not quantified:
        suggestions.append({
            "title": "Add measurable outcomes",
            "body": "Strengthen bullet points with numbers: time saved, revenue influenced, users supported, or quality improved.",
        })

    used_verbs = set(re.findall(r"\b[a-z]+\b", resume_lower)) & ACTION_VERBS
    if len(used_verbs) < 3:
        suggestions.append({
            "title": "Lead with stronger action verbs",
            "body": "Start experience bullets with verbs such as built, automated, improved, launched, or optimized to make ownership clear.",
        })

    if len(resume_text.split()) < 180:
        suggestions.append({
            "title": "Add a little more context",
            "body": "Your resume is concise. Add one or two role-specific bullets that show scope, tools, and the outcome of your work.",
        })

    if missing_skills and any(term in job_lower for term in ("team", "collaborat", "communicat")):
        suggestions.append({
            "title": "Show how you work with others",
            "body": "Include a bullet about cross-functional collaboration, stakeholder communication, mentoring, or leading delivery.",
        })

    if score >= 75 and len(suggestions) < 3:
        suggestions.append({
            "title": "Make the strongest match easy to scan",
            "body": f"Your profile already aligns well with this role. Put your {', '.join(matching_skills[:2]) or 'most relevant strengths'} near the top.",
        })

    return suggestions[:4]


def analyze_resume(resume_text: str, job_description: str) -> dict:
    resume_text = resume_text.strip()
    job_description = job_description.strip()
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    matching_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform([resume_text, job_description])
        similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:
        similarity = 0.0

    # Keep the score explainable: TF-IDF is primary, with a small skills signal
    # so a skills-heavy job description is not penalised for short wording.
    skill_signal = len(matching_skills) / len(job_skills) if job_skills else 0.0
    score = round(max(0.0, min(100.0, (similarity * 0.7 + skill_signal * 0.3) * 100)))
    top_keywords = _top_keywords(job_description, resume_text) if resume_text else []
    suggestions = make_suggestions(
        resume_text,
        job_description,
        matching_skills,
        missing_skills,
        score,
    )

    if score >= 80:
        summary = "Strong alignment. Your resume already speaks to many of the role’s priorities."
        label = "Strong match"
    elif score >= 60:
        summary = "Good foundation. A few targeted edits could make your experience more visible."
        label = "Good match"
    elif score >= 40:
        summary = "Some overlap is present. Use the gaps below to tailor your resume before applying."
        label = "Potential match"
    else:
        summary = "The overlap is limited right now. Focus on the missing skills and role-specific evidence."
        label = "Needs tailoring"

    return {
        "score": score,
        "label": label,
        "summary": summary,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "top_keywords": top_keywords,
        "resume_word_count": len(resume_text.split()),
        "job_word_count": len(job_description.split()),
        "skill_count": len(job_skills),
    }