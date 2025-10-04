from fastapi import APIRouter, HTTPException
from models import Donation
from database import donations

router = APIRouter()

@router.post("/donations")
def create_donation(donation: Donation):
    donations.append(donation)
    return {"message": "Donation added successfully", "donation": donation}

@router.get("/donations")
def get_donations():
    return donations

@router.get("/donations/{donation_id}")
def get_donation(donation_id: int):
    for d in donations:
        if d.id == donation_id:
            return d
    raise HTTPException(status_code=404, detail="Donation not found")
