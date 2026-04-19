from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.resume import Resume
from models.job_opening import JobOpening
from models.application import Application
from fastapi import Query

router = APIRouter()


# -----------------------------------
# GET APPLICANTS FOR JOB
# -----------------------------------


@router.get("/applicants/{job_id}")
def get_applicants(job_id: int, db: Session = Depends(get_db)):

    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).all()

    result = []

    for app in applications:

        resume = db.query(Resume).filter(
            Resume.id == app.resume_id
        ).first()

        result.append({
            "id": app.id,
            "candidate_email": app.candidate_email,
            "status": app.status,
            "resume": resume
        })

    return result


# -----------------------------------
# MARK RESUME REVIEWED
# -----------------------------------
@router.post("/review/{resume_id}")
def review_resume(resume_id: int, db: Session = Depends(get_db)):

    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    resume.status = "Reviewed"

    db.commit()

    return {"message": "Resume reviewed"}


# -----------------------------------
# SEND RESULTS
# -----------------------------------
@router.post("/send-results/{job_id}")
def send_results(job_id: int, db: Session = Depends(get_db)):

    resumes = db.query(Resume).filter(
        Resume.opening_id == job_id
    ).all()

    # ensure all reviewed
    for r in resumes:
        if r.status != "Reviewed":
            return {"error": "All resumes must be reviewed first"}

    # sort by score
    resumes_sorted = sorted(resumes, key=lambda x: x.score, reverse=True)

    for i, r in enumerate(resumes_sorted):

        if i == 0:
            r.decision = "Accepted"
        else:
            r.decision = "Rejected"

        r.results_sent = True

    db.commit()

    return {"message": "Results sent"}

@router.get("/jobs/{email}")
def get_recruiter_jobs(email:str, db:Session=Depends(get_db)):

    jobs = db.query(JobOpening).filter(
        JobOpening.recruiter_email == email
    ).all()

    return jobs


@router.put("/update_status/{id}")
def update_status(
    id: int,
    status: str = Query(...),
    db: Session = Depends(get_db)
):

    application = db.query(Application).filter(
        Application.id == id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
            
        )
        

    application.status = status

    db.commit()

    return {"message": "updated"}

