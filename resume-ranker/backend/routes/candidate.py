import os
import shutil

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from models.resume import Resume
from models.job_opening import JobOpening

from services.parser import parse_resume
from services.ranker import rank_resume
from services.rag_explainer import generate_rag_explanation


router = APIRouter(
    prefix="/resumes",
    tags=["Resume Upload"]
)

UPLOAD_FOLDER = "uploaded_resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
def upload_resume(
    email: str = Form(...),
    opening_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse
    opening = db.query(JobOpening).get(opening_id)

    parsed_data = parse_resume(
        file_path,
        opening.title.lower()
    )

    # Rank
    evaluation = rank_resume(
        parsed_data,
        opening
    )

    # Explainability
    explanation = generate_rag_explanation(
        parsed_data,
        opening,
        evaluation
    )

    resume = Resume(
        email=email,
        filename=file.filename,
        opening_id=opening_id,
        score=evaluation["score"],
        skill_match=evaluation["skill_match"],
        experience_match=evaluation["experience_match"],
        missing_skills=evaluation["missing_skills"],
        rag_explanation=explanation,
        status="Reviewed"
    )

    db.add(resume)
    db.commit()

    return {"message": "Uploaded & Reviewed"}
