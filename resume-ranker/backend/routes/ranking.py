from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.application import Application
from models.resume import Resume

router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get("/opening/{opening_id}")
def get_ranking_by_opening(opening_id: int, db: Session = Depends(get_db)):

    results = (
    db.query(Application, Resume)
    .join(Resume, Resume.email == Application.candidate_email)
    .filter(Application.job_id == opening_id)
    .filter(Resume.opening_id == opening_id)
    .order_by(Application.score.desc())
    .all()
)

    result = []
    rank = 1

    for app, res in results:

        result.append({
            "id": app.id,
            "rank": rank,
            "email": app.candidate_email,
            "score": app.score,
            "skill_match": app.skill_match,
            "experience_match": app.experience_match,
            "status": app.status,
            "missing_skills": app.missing_skills,
            "rag_explanation": res.rag_explanation
        })

        rank += 1

    return result