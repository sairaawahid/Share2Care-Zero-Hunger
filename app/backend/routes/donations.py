from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import Donation
from db import get_session

router = APIRouter()


@router.post("/donations")
def create_donation(donation: Donation, session: Session = Depends(get_session)):
    session.add(donation)
    session.commit()
    session.refresh(donation)
    return {"message": "Donation added successfully", "donation": donation}


@router.get("/donations")
def get_donations(session: Session = Depends(get_session)):
    donations = session.exec(select(Donation)).all()
    return donations


@router.get("/donations/{donation_id}")
def get_donation(donation_id: int, session: Session = Depends(get_session)):
    donation = session.get(Donation, donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    return donation
