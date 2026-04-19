from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from models.resume import Resume

router = APIRouter(
    prefix="/candidate",
    tags=["Candidate Dashboard"]
)


# Candidate sees review status
@router.get("/applications/{email}")
def get_applications(
    email: str,
    db: Session = Depends(get_db)
):

    resumes = db.query(Resume).filter(
        Resume.candidate_email == email
    ).all()

    return resumes
