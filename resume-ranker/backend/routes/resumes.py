# ---------------------------------------------------
# RESUME ROUTES — ROLE FOLDER STORAGE
# ---------------------------------------------------

import os
import shutil

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from services.llm_advisor import generate_llm_advice

from database.db import get_db
from models.resume import Resume
from models.job_opening import JobOpening

from services.parser import parse_resume
from services.ranker import rank_resume
from services.rag_explainer import generate_rag_explanation

router = APIRouter()

UPLOAD_BASE = "uploaded_resumes"


# ---------------------------------------------------
# UPLOAD RESUME
# ---------------------------------------------------
@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    email: str = Form(...),
    opening_id: int = Form(...),
    db: Session = Depends(get_db)
):

    # ---------------------------------------------------
    # 1️⃣ GET JOB OPENING
    # ---------------------------------------------------
    job = db.query(JobOpening).filter(
        JobOpening.id == opening_id
    ).first()

    if not job:
        return {"error": "Invalid Job Opening ID"}

    role_name = job.title.replace(" ", "_")

    # ---------------------------------------------------
    # 2️⃣ CREATE ROLE FOLDER IF NOT EXISTS
    # ---------------------------------------------------
    role_folder = os.path.join(
        UPLOAD_BASE,
        role_name
    )

    os.makedirs(role_folder, exist_ok=True)

    # ---------------------------------------------------
    # 3️⃣ SAVE FILE IN ROLE FOLDER
    # ---------------------------------------------------
    file_path = os.path.join(
        role_folder,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print("Saved to:", file_path)

    # ---------------------------------------------------
    # 4️⃣ PARSE RESUME
    # ---------------------------------------------------
    parsed = parse_resume(file_path, job.title)

    print("Parsed:", parsed)

    # ---------------------------------------------------
    # 5️⃣ RANK RESUME
    # ---------------------------------------------------
    ranking = rank_resume(parsed, job)

    print("Ranking:", ranking)

    # ---------------------------------------------------
    # 6️⃣ LLM RESUME ADVICE (SAFE MODE)
    # ---------------------------------------------------
    try:

        llm_feedback = generate_llm_advice(
            parsed,
            job,
            ranking
        )

    except Exception as e:

        print("LLM ERROR:", e)

        llm_feedback = "AI resume advice temporarily unavailable."

    # ---------------------------------------------------
    # 7️⃣ RAG EXPLAINABILITY
    # ---------------------------------------------------
    rag_text = generate_rag_explanation(
        parsed,
        job,
        ranking
    )

    # ---------------------------------------------------
    # 8️⃣ SAVE TO DATABASE
    # ---------------------------------------------------
    new_resume = Resume(
        email=email,
        filename=file.filename,
        opening_id=opening_id,
        score=ranking["score"],
        skill_match=ranking["skill_match"],
        experience_match=ranking["experience_match"],
        missing_skills=ranking["missing_skills"],
        rag_explanation=rag_text,
        status="Reviewed"
    )

    db.add(new_resume)
    db.commit()

    # ---------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------
    return {
        "message": "Resume uploaded + parsed + ranked",
        "stored_in": role_folder,
        "score": ranking["score"],
        "skill_match": ranking["skill_match"],
        "experience_match": ranking["experience_match"],
        "missing_skills": ranking["missing_skills"],
        "rag_explanation": rag_text,
        "llm_feedback": llm_feedback
    }