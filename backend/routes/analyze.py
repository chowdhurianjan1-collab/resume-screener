from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import schemas, db_models
from services import nlp_engine
from services.pdf_extractor import extract_contact_info

router = APIRouter()


def _profile_dict(profile: db_models.SkillProfile) -> dict:
    return {
        "required_skills": profile.required_skills or {},
        "preferred_skills": profile.preferred_skills or {},
        "min_experience_years": profile.min_experience_years or 0,
    }


@router.post("/analyze", response_model=schemas.AnalyzeResponse)
def analyze(payload: schemas.AnalyzeRequest, db: Session = Depends(get_db)):
    resumes = [r for r in payload.resumes if r and r.strip()]
    if not payload.job_description.strip():
        raise HTTPException(400, "job_description is required")
    if not resumes:
        raise HTTPException(400, "At least one non-empty resume is required")

    names = payload.names or []
    while len(names) < len(resumes):
        names.append(f"Candidate {len(names) + 1}")

    profile = None
    profile_row = None
    if payload.profile_id is not None:
        profile_row = db.query(db_models.SkillProfile).get(payload.profile_id)
        if not profile_row:
            raise HTTPException(404, "Skill profile not found")
        profile = _profile_dict(profile_row)

    run = db_models.AnalysisRun(
        profile_id=profile_row.id if profile_row else None,
        job_description=payload.job_description,
    )
    db.add(run)
    db.flush()

    results_out = []
    for resume_text, name in zip(resumes, names):
        scored = nlp_engine.score_candidate(payload.job_description, resume_text, profile)
        email, phone = extract_contact_info(resume_text)
        summary = nlp_engine.build_summary(name, scored)

        row = db_models.CandidateResult(
            run_id=run.id,
            name=name,
            overall_score=scored["overall_score"],
            semantic_score=scored["semantic_score"],
            skill_score=scored["skill_score"],
            experience_years=scored["experience_years"],
            matched_skills=scored["matched_skills"],
            missing_skills=scored["missing_skills"],
            extracted_email=email,
            extracted_phone=phone,
            raw_text_excerpt=resume_text[:500],
        )
        db.add(row)
        results_out.append(schemas.CandidateResultOut(
            name=name,
            overall_score=scored["overall_score"],
            semantic_score=scored["semantic_score"],
            skill_score=scored["skill_score"],
            experience_years=scored["experience_years"],
            matched_skills=scored["matched_skills"],
            missing_skills=scored["missing_skills"],
            extracted_email=email,
            extracted_phone=phone,
            summary=summary,
        ))

    db.commit()

    jd_skills = (
        list(profile["required_skills"].keys()) + list(profile["preferred_skills"].keys())
        if profile else nlp_engine.extract_skills(payload.job_description, nlp_engine.DEFAULT_SKILLS)
    )

    results_out.sort(key=lambda r: r.overall_score, reverse=True)
    return schemas.AnalyzeResponse(run_id=run.id, results=results_out, jd_skills_detected=jd_skills)
