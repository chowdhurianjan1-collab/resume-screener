from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models import schemas, db_models
from services import nlp_engine
from services.pdf_extractor import extract_text, extract_contact_info, guess_candidate_name

router = APIRouter()

MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB per resume


@router.post("/upload-analyze", response_model=schemas.AnalyzeResponse)
async def upload_and_analyze(
    job_description: str = Form(...),
    profile_id: Optional[int] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Scan uploaded resume files (PDF/DOCX/TXT), extract text, and score
    each candidate against the job description in one call."""
    if not job_description.strip():
        raise HTTPException(400, "job_description is required")
    if not files:
        raise HTTPException(400, "At least one file is required")

    profile = None
    profile_row = None
    if profile_id is not None:
        profile_row = db.query(db_models.SkillProfile).get(profile_id)
        if not profile_row:
            raise HTTPException(404, "Skill profile not found")
        profile = {
            "required_skills": profile_row.required_skills or {},
            "preferred_skills": profile_row.preferred_skills or {},
            "min_experience_years": profile_row.min_experience_years or 0,
        }

    run = db_models.AnalysisRun(
        profile_id=profile_row.id if profile_row else None,
        job_description=job_description,
    )
    db.add(run)
    db.flush()

    results_out = []
    for upload in files:
        raw = await upload.read()
        if len(raw) > MAX_FILE_SIZE:
            raise HTTPException(413, f"{upload.filename} exceeds 8MB limit")
        try:
            text = extract_text(upload.filename, raw)
        except ValueError as e:
            raise HTTPException(400, str(e))
        if not text.strip():
            raise HTTPException(400, f"Could not extract any text from {upload.filename}")

        name = guess_candidate_name(text, fallback=upload.filename)
        scored = nlp_engine.score_candidate(job_description, text, profile)
        email, phone = extract_contact_info(text)
        summary = nlp_engine.build_summary(name, scored)

        row = db_models.CandidateResult(
            run_id=run.id,
            name=name,
            source_filename=upload.filename,
            overall_score=scored["overall_score"],
            semantic_score=scored["semantic_score"],
            skill_score=scored["skill_score"],
            experience_years=scored["experience_years"],
            matched_skills=scored["matched_skills"],
            missing_skills=scored["missing_skills"],
            extracted_email=email,
            extracted_phone=phone,
            raw_text_excerpt=text[:500],
        )
        db.add(row)
        results_out.append(schemas.CandidateResultOut(
            name=name,
            source_filename=upload.filename,
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
        if profile else nlp_engine.extract_skills(job_description, nlp_engine.DEFAULT_SKILLS)
    )

    results_out.sort(key=lambda r: r.overall_score, reverse=True)
    return schemas.AnalyzeResponse(run_id=run.id, results=results_out, jd_skills_detected=jd_skills)
