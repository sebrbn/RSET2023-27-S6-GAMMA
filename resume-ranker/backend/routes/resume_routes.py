from fastapi import HTTPException
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import shutil
import os

from database.db import get_db
from models.resume import Resume
from models.job_opening import JobOpening
from models.application import Application


from services.parser import parse_resume
from services.ranker import rank_resume
from services.rag_explainer import generate_rag_explanation
from services.llm_advisor import generate_llm_advice

router = APIRouter()

UPLOAD_BASE = "uploaded_resumes"


# -----------------------------------------
# UPLOAD RESUME
# -----------------------------------------
@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    email: str = Form(...),
    opening_id: int = Form(...),
    db: Session = Depends(get_db)
):

    job = db.query(JobOpening).filter(
        JobOpening.id == opening_id
    ).first()

    if not job:
        return {"error": "Invalid job"}

    role_name = job.title.replace(" ", "_")

    role_folder = os.path.join(UPLOAD_BASE, role_name)

    os.makedirs(role_folder, exist_ok=True)

    file_path = os.path.join(role_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed = parse_resume(file_path, job.title)

    ranking = rank_resume(parsed, job)

    llm_feedback = generate_llm_advice(parsed,job,ranking)

    application = Application(
    candidate_email=email,
    job_id=opening_id,
    score=ranking["score"],
    skill_match=ranking["skill_match"],
    experience_match=ranking["experience_match"],
    missing_skills=ranking["missing_skills"],
    status="pending",
    llm_feedback=llm_feedback
)

    db.add(application)
    db.commit()

    rag_text = generate_rag_explanation(parsed, job, ranking)

    new_resume = Resume(
        email=email,
        filename=file.filename,
        opening_id=opening_id,
        score=ranking["score"],
        skill_match=ranking["skill_match"],
        experience_match=ranking["experience_match"],
        missing_skills=str(ranking["missing_skills"]),
        rag_explanation=rag_text,
        status="Processing",
        decision="Pending",
        results_sent=False
    )

    db.add(new_resume)
    db.commit()

    return {"message": "Resume uploaded"}



@router.get("/view/{email}")
def view_resume(email: str, db: Session = Depends(get_db)):

    resume = db.query(Resume).filter(
        Resume.email == email
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Search in all job folders
    for folder in os.listdir(UPLOAD_BASE):

        file_path = os.path.join(
            UPLOAD_BASE,
            folder,
            resume.filename
        )

        if os.path.exists(file_path):
            return FileResponse(file_path)

    raise HTTPException(
        status_code=404,
        detail="Resume file not found on server"
    )
