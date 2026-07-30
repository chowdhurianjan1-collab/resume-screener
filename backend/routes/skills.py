from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import schemas, db_models

router = APIRouter()


@router.post("/skill-profiles", response_model=schemas.SkillProfileOut)
def create_profile(payload: schemas.SkillProfileCreate, db: Session = Depends(get_db)):
    """Let a company define which skills matter for a given role, and how
    much each one is weighted. Used by /analyze and /upload-analyze to
    customize scoring instead of relying on the generic skill list."""
    row = db_models.SkillProfile(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/skill-profiles", response_model=List[schemas.SkillProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(db_models.SkillProfile).order_by(db_models.SkillProfile.created_at.desc()).all()


@router.get("/skill-profiles/{profile_id}", response_model=schemas.SkillProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    row = db.query(db_models.SkillProfile).get(profile_id)
    if not row:
        raise HTTPException(404, "Skill profile not found")
    return row


@router.put("/skill-profiles/{profile_id}", response_model=schemas.SkillProfileOut)
def update_profile(profile_id: int, payload: schemas.SkillProfileCreate, db: Session = Depends(get_db)):
    row = db.query(db_models.SkillProfile).get(profile_id)
    if not row:
        raise HTTPException(404, "Skill profile not found")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/skill-profiles/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    row = db.query(db_models.SkillProfile).get(profile_id)
    if not row:
        raise HTTPException(404, "Skill profile not found")
    db.delete(row)
    db.commit()
    return {"ok": True}
