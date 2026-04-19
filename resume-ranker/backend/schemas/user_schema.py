# ---------------------------------------------------
# USER SCHEMAS
# ---------------------------------------------------

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str # recruiter / candidate


class UserLogin(BaseModel):
    email: EmailStr
    password: str