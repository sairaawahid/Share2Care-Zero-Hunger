from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel import Session
from app.backend.database import get_session
from app.backend import models

router = APIRouter(prefix="/api/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
def register(user_in: models.UserCreate, session: Session = Depends(get_session)):
    # check existing email
    existing = session.exec(select(models.User).where(models.User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(user_in.password)
    user = models.User(name=user_in.name, email=user_in.email, password=hashed, role=user_in.role or "donor")
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered", "user": user}

@router.post("/login")
def login(credentials: models.UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(models.User).where(models.User.email == credentials.email)).first()
    if not user or not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # simple response; expand with JWT later
    return {"message": "Login successful", "user_id": user.id, "role": user.role}

