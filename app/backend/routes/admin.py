from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.backend.database import get_session
from sqlmodel import Session
from app.backend import models

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users")
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(models.User)).all()

@router.get("/donations")
def list_donations(session: Session = Depends(get_session)):
    return session.exec(select(models.Donation)).all()

@router.get("/communities")
def list_communities(session: Session = Depends(get_session)):
    return session.exec(select(models.Community)).all()
