from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import SessionLocal
from models.job_role import JobRole

router = APIRouter(prefix="/roles", tags=["Job Roles"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Add role
@router.post("/add")
def add_role(name: str, description: str, db: Session = Depends(get_db)):

    role = JobRole(name=name, description=description)

    db.add(role)
    db.commit()
    db.refresh(role)

    return {"message": "Role added successfully"}


# Get all roles
@router.get("/all")
def get_roles(db: Session = Depends(get_db)):
    return db.query(JobRole).all()
