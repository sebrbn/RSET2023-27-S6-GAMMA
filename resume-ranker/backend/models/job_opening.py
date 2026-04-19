# ---------------------------------------------------
# JOB OPENING DATABASE MODEL
# ---------------------------------------------------

from sqlalchemy import Column, Integer, String, Text
from database.db import Base


class JobOpening(Base):

    __tablename__ = "job_openings"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    company = Column(String)
    department = Column(String)
    description = Column(Text)

    # Store required skills as JSON string
    required_skills = Column(Text)

    experience_required = Column(Integer)

    recruiter_email = Column(String)
