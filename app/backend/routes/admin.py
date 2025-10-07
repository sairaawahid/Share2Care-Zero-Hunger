from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import User, Donation, Community
from db import get_session

router = APIRouter()


@router.get("/admin/users")
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted"}


@router.get("/admin/donations")
def list_donations(session: Session = Depends(get_session)):
    donations = session.exec(select(Donation)).all()
    return donations


@router.get("/admin/communities")
def list_communities(session: Session = Depends(get_session)):
    communities = session.exec(select(Community)).all()
    return communities
