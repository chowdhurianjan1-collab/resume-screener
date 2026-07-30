"""
db_models.py — persisted tables.

- SkillProfile: a company's customized skill taxonomy (required / preferred
  skills, weights, aliases). Lets each company tune what "good candidate"
  means for them instead of a single hardcoded skill list.
- AnalysisRun: a saved screening run (JD + settings) so history can be
  retrieved later.
- CandidateResult: one scored candidate belonging to an AnalysisRun.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base


class SkillProfile(Base):
    __tablename__ = "skill_profiles"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False)
    role_title = Column(String(200), nullable=False)
    # e.g. {"python": 3, "fastapi": 3, "docker": 2, "aws": 2, "graphql": 1}
    # higher weight = more important to this company for this role
    required_skills = Column(JSON, default=dict)
    preferred_skills = Column(JSON, default=dict)
    # extra plain-text notes injected into scoring (e.g. "prefers fintech background")
    notes = Column(Text, default="")
    min_experience_years = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    runs = relationship("AnalysisRun", back_populates="profile")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("skill_profiles.id"), nullable=True)
    job_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("SkillProfile", back_populates="runs")
    candidates = relationship("CandidateResult", back_populates="run", cascade="all, delete-orphan")


class CandidateResult(Base):
    __tablename__ = "candidate_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False)
    name = Column(String(200))
    source_filename = Column(String(300), nullable=True)
    overall_score = Column(Float)
    semantic_score = Column(Float)
    skill_score = Column(Float)
    experience_years = Column(Float, nullable=True)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    extracted_email = Column(String(200), nullable=True)
    extracted_phone = Column(String(50), nullable=True)
    raw_text_excerpt = Column(Text, nullable=True)

    run = relationship("AnalysisRun", back_populates="candidates")
