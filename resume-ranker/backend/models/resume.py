from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database.db import Base

class Resume(Base):

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String)
    filename = Column(String)

    opening_id = Column(Integer, ForeignKey("job_openings.id"))

    score = Column(Float)

    skill_match = Column(Float)
    experience_match = Column(Float)

    missing_skills = Column(String)
    rag_explanation = Column(String)

    status = Column(String, default="Processing")

    decision = Column(String, default="Pending")

    results_sent = Column(Boolean, default=False)