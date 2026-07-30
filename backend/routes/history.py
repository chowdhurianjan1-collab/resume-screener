from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import schemas, db_models

router = APIRouter()


@router.get("/history", response_model=List[schemas.RunSummaryOut])
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(db_models.AnalysisRun).order_by(db_models.AnalysisRun.created_at.desc()).limit(50).all()
    out = []
    for run in runs:
        candidates = sorted(run.candidates, key=lambda c: c.overall_score, reverse=True)
        top = candidates[0] if candidates else None
        out.append(schemas.RunSummaryOut(
            id=run.id,
            created_at=run.created_at.isoformat(),
            candidate_count=len(candidates),
            top_candidate=top.name if top else None,
            top_score=top.overall_score if top else None,
        ))
    return out


@router.get("/history/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(db_models.AnalysisRun).get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    candidates = sorted(run.candidates, key=lambda c: c.overall_score, reverse=True)
    return {
        "id": run.id,
        "created_at": run.created_at.isoformat(),
        "job_description": run.job_description,
        "results": [
            {
                "name": c.name,
                "source_filename": c.source_filename,
                "overall_score": c.overall_score,
                "semantic_score": c.semantic_score,
                "skill_score": c.skill_score,
                "experience_years": c.experience_years,
                "matched_skills": c.matched_skills,
                "missing_skills": c.missing_skills,
                "extracted_email": c.extracted_email,
                "extracted_phone": c.extracted_phone,
            }
            for c in candidates
        ],
    }
