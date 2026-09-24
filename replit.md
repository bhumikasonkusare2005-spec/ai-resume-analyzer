# AI Resume Analyzer

A Flask app that compares a PDF resume with a pasted job description and returns an explainable match score, skills overlap, and tailoring suggestions.

## Run & Operate

- `pnpm --filter @workspace/resume-analyzer run dev` — run the Flask resume analyzer
- `python artifacts/resume-analyzer/app.py` — run the Flask app directly
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `PORT` is injected by the artifact workflow; `SESSION_SECRET` is optional and used for Flask flash messages

## Stack

- Python 3, Flask, PyPDF2, scikit-learn
- pnpm workspace wrapper for Replit workflow execution

## Where things live

- `artifacts/resume-analyzer/app.py` — Flask entry point and upload route
- `artifacts/resume-analyzer/analyzer.py` — TF-IDF/cosine similarity and skill matching
- `artifacts/resume-analyzer/templates/index.html` — Jinja interface
- `artifacts/resume-analyzer/static/` — responsive styling and upload enhancements
- `artifacts/resume-analyzer/README.md` — local setup and product notes

## Architecture decisions

- Keep the app monolithic in Flask because the requested product is a focused upload-and-analyze flow.
- Use an editable skill alias dictionary rather than a black-box model so detected matches are easy to explain and tune.
- Weight TF-IDF/cosine similarity at 70% and detected skill overlap at 30% for a score that reflects both language fit and explicit requirements.
- Read PDF bytes in memory and never persist the upload.

## Product

- Upload a PDF resume
- Paste a job description
- Receive a match score, matching skills, missing skills, keywords, and improvement suggestions

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
