from typing import List, Dict, Optional
from pydantic import BaseModel, Field


# ── Skill Profiles (company customization) ─────────────────────────────────
class SkillProfileCreate(BaseModel):
    company_name: str
    role_title: str
    required_skills: Dict[str, int] = Field(
        default_factory=dict,
        description="skill -> weight (1-3). Weight 3 = critical, 1 = nice-to-have-but-required",
    )
    preferred_skills: Dict[str, int] = Field(default_factory=dict)
    notes: str = ""
    min_experience_years: int = 0


class SkillProfileOut(SkillProfileCreate):
    id: int

    class Config:
        from_attributes = True


# ── Analyze (text-based, no files) ──────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    job_description: str
    resumes: List[str]
    names: List[str] = Field(default_factory=list)
    profile_id: Optional[int] = None  # use a saved company skill profile if provided


class CandidateResultOut(BaseModel):
    name: str
    source_filename: Optional[str] = None
    overall_score: float
    semantic_score: float
    skill_score: float
    experience_years: Optional[float] = None
    matched_skills: List[str]
    missing_skills: List[str]
    extracted_email: Optional[str] = None
    extracted_phone: Optional[str] = None
    summary: str

    class Config:
        from_attributes = True


class AnalyzeResponse(BaseModel):
    run_id: int
    results: List[CandidateResultOut]
    jd_skills_detected: List[str]


# ── History ──────────────────────────────────────────────────────────────
class RunSummaryOut(BaseModel):
    id: int
    created_at: str
    candidate_count: int
    top_candidate: Optional[str] = None
    top_score: Optional[float] = None
