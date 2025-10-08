from fastapi import APIRouter, Depends
from sqlmodel import select, Session
from app.backend.database import get_session
from app.backend import models

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users", response_model=list[models.UserRead])
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(models.User)).all()

@router.get("/donations", response_model=list[models.DonationRead])
def list_donations(session: Session = Depends(get_session)):
    return session.exec(select(models.Donation)).all()

@router.get("/communities", response_model=list[models.CommunityRead])
def list_communities(session: Session = Depends(get_session)):
    return session.exec(select(models.Community)).all()
