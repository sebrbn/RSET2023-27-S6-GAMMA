# ---------------------------------------------------
# JOB OPENINGS ROUTES — WITH AUTO FOLDER CREATION
# ---------------------------------------------------

import os
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from models.job_opening import JobOpening

router = APIRouter()

UPLOAD_BASE = "uploaded_resumes"


# ---------------------------------------------------
# ADD JOB OPENING
# ---------------------------------------------------
@router.post("/add")
def add_opening(opening: dict, db: Session = Depends(get_db)):

    # Extract skills safely
    skills = opening.get("required_skills", [])

    # If frontend sends string
    if isinstance(skills, str):
        flat_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]

    # If frontend sends list
    elif isinstance(skills, list):
        flat_skills = [str(s).strip().lower() for s in skills if str(s).strip()]

    else:
        flat_skills = []

    # Create DB object
    new_opening = JobOpening(
        title=opening["title"],
        company=opening.get("company"),
        department=opening.get("department"),
        description=opening.get("description"),
        required_skills=json.dumps(flat_skills),
        experience_required=opening.get("experience_required", 0),
        recruiter_email=opening.get("recruiter_email")
    )

    db.add(new_opening)
    db.commit()
    db.refresh(new_opening)

    return {
        "message": "Job opening added",
        "job_id": new_opening.id
    }

    # ---------------------------------------------------
    # 🆕 CREATE FOLDER FOR THIS JOB ROLE
    # ---------------------------------------------------
    role_folder = os.path.join(
        UPLOAD_BASE,
        opening["title"].replace(" ", "_")
    )

    os.makedirs(role_folder, exist_ok=True)

    return {
        "message": "Job opening added + folder created",
        "folder": role_folder,
        "job_id": new_opening.id
    }


# ---------------------------------------------------
# GET ALL OPENINGS
# ---------------------------------------------------
@router.get("/all")
def get_all_openings(db: Session = Depends(get_db)):

    openings = db.query(JobOpening).all()

    result = []

    for job in openings:

        # Safely parse skills JSON
        try:
            skills = json.loads(job.required_skills) \
                     if job.required_skills else []
        except:
            skills = []

        result.append({
            "id": job.id,
            "title": job.title,
            "department": job.department,
            "description": job.description,
            "required_skills": skills,
            "experience_required":
                job.experience_required
        })

    return result


# ---------------------------------------------------
# GET SINGLE OPENING
# ---------------------------------------------------
@router.get("/{opening_id}")
def get_opening(
    opening_id: int,
    db: Session = Depends(get_db)
):

    o = db.query(JobOpening).filter(
        JobOpening.id == opening_id
    ).first()

    if not o:
        raise HTTPException(
            status_code=404,
            detail="Opening not found"
        )

    return {

    "id": o.id,
    "title": o.title,
    "department": o.department,
    "description": o.description,

    "required_skills": (
        o.required_skills.split(",")
        if isinstance(o.required_skills, str)
        else o.required_skills
    ) if o.required_skills else [],

    "experience_required": o.experience_required
}
