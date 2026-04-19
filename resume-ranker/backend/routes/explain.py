from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db

from models.resume import Resume
from models.job_role import JobRole

from services.rag_engine import generate_explanation

router = APIRouter()


# ---------------------------------------------------
# EXPLAIN CANDIDATE RANK
# ---------------------------------------------------
@router.get("/{resume_id}")
def explain_candidate(
    resume_id: int,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume)\
        .filter(Resume.id == resume_id)\
        .first()

    if not resume:
        return {"error": "Resume not found"}

    job_role = db.query(JobRole)\
        .filter(JobRole.name == resume.role)\
        .first()

    explanation = generate_explanation(
        resume.skills.split(","),
        resume.experience,
        job_role.description
    )

    return {
        "resume_id": resume_id,
        "explanation": explanation
    }
