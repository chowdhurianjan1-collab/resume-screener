"""
main.py — FastAPI entrypoint for the AI Resume Screener backend.

Endpoints:
  POST /api/analyze          — score pasted resume text against a JD
  POST /api/upload-analyze   — upload PDF/DOCX/TXT resumes, scan + score
  CRUD /api/skill-profiles   — company-customized skill taxonomies
  GET  /api/history          — past analysis runs
  GET  /health               — liveness check
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import analyze, upload, skills, history

app = FastAPI(
    title="AI Resume Screener",
    description="Company-customizable resume screening: upload resumes, scan them, "
                 "and rank candidates against a job description and a per-company skill profile.",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Also allow any Vercel preview/production URL for this project out of the
    # box, so preview deployments don't need ALLOWED_ORIGINS updated by hand.
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"[startup] CORS allow_origins={ALLOWED_ORIGINS} (+ *.vercel.app)")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(skills.router, prefix="/api", tags=["skill-profiles"])
app.include_router(history.router, prefix="/api", tags=["history"])
