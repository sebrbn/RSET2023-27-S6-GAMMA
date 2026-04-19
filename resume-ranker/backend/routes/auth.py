# ---------------------------------------------------
# AUTH ROUTES — FINAL FIXED VERSION
# ---------------------------------------------------

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas import UserSignup

from database.db import get_db
from models.user import User
from fastapi import Body

# ✅ Correct import
from services.security import (
    hash_password,
    verify_password
)

router = APIRouter()

# ---------------------------------------------------
# SIGNUP
# ---------------------------------------------------
@router.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):

    # Check existing user
    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    try:
        hashed_pw = hash_password(user.password)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    new_user = User(
        email=user.email,
        password=hashed_pw,
        role=user.role
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User created successfully"
    }

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@router.post("/login")
def login(
    email: str = Body(...),
    password: str = Body(...),
    
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return {
        "message": "Login successful",
        "role": user.role
    }