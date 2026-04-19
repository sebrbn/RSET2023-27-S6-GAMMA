from sqlalchemy import Column, Integer, String, ForeignKey
from database.db import Base


class Application(Base):

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)

    candidate_email = Column(String)

    job_id = Column(Integer, ForeignKey("job_openings.id"))

    status = Column(String, default="pending")

    score = Column(Integer, nullable=True)

    skill_match = Column(Integer, nullable=True)

    experience_match = Column(Integer, nullable=True)

    missing_skills = Column(String, nullable=True)

    llm_feedback = Column(String)