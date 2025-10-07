from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.backend.models import User, UserLogin
from app.backend.db import get_session

router = APIRouter()


@router.post("/register")
def register(user: User, session: Session = Depends(get_session)):
    # Check if email already exists
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered successfully", "user": user}


@router.post("/login")
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(
        select(User).where(User.email == user_login.email, User.password == user_login.password)
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user": db_user}

