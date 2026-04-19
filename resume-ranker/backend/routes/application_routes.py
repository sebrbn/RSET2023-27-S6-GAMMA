from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.application import Application
from models.job_opening import JobOpening

router = APIRouter()


@router.get("/candidate/{email}")
def get_candidate_applications(email: str, db: Session = Depends(get_db)):

    apps = db.query(Application).filter(
        Application.candidate_email == email
    ).all()

    result = []

    for a in apps:

        job = db.query(JobOpening).filter(
            JobOpening.id == a.job_id
        ).first()

        result.append({

            "job_title": job.title,
            "department": job.department,

            "status": a.status,

            "skill_match": a.skill_match,
            "experience_match": a.experience_match,
            "missing_skills": a.missing_skills,

            # ranking visible only after decision
            "score": a.score if a.status != "pending" else None,

            "llm_feedback" : a.llm_feedback
        })

    return result

@router.put("/update_status/{id}")
def update_status(id: int, status: str, db: Session = Depends(get_db)):

    app = db.query(Application).filter(
        Application.id == id
    ).first()

    if not app:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    if status not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    app.status = status

    db.commit()

    return {
        "message": "Application updated",
        "status": status
    }