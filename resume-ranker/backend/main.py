# ---------------------------------------------------
# MAIN FASTAPI ENTRY
# ---------------------------------------------------
from dotenv import load_dotenv
import os
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import engine, Base
from models.job_opening import JobOpening
from models.resume import Resume


# Import routers
from routes import (
    job_openings,
    resumes,
    auth,
    candidate,
    ranking,
    application_routes
)

from routes import resume_routes
from routes import recruiter_routes




# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Ranker"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Register routers
app.include_router(
    job_openings.router,
    prefix="/openings",
    tags=["Job Openings"]
)

app.include_router(
    application_routes.router,
    prefix="/applications"
)

app.include_router(
    recruiter_routes.router,
    prefix="/recruiter"
)

app.include_router(
    resume_routes.router,
    prefix="/resumes"
)

app.include_router(
    resumes.router,
    prefix="/resumes",
    tags=["Resume Upload"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    candidate.router
)
app.include_router(
    ranking.router
)


@app.get("/")
def root():
    return {
        "message":
        "Resume Ranker Backend Running"
    }
