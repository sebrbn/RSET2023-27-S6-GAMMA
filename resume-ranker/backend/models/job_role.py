from sqlalchemy import Column, Integer, String
from database.db import Base


class JobRole(Base):

    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
