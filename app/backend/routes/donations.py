from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel import Session
from typing import List
from app.backend.database import get_session
from app.backend import models

router = APIRouter(prefix="/api/donations", tags=["Donations"])

@router.post("/", response_model=models.Donation)
def create_donation(payload: models.DonationCreate, session: Session = Depends(get_session)):
    donation = models.Donation.from_orm(payload)
    session.add(donation)
    session.commit()
    session.refresh(donation)
    return donation

@router.get("/", response_model=List[models.Donation])
def list_donations(session: Session = Depends(get_session)):
    return session.exec(select(models.Donation)).all()

@router.get("/{donation_id}", response_model=models.Donation)
def get_donation(donation_id: int, session: Session = Depends(get_session)):
    donation = session.get(models.Donation, donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    return donation

@router.put("/{donation_id}/claim")
def claim_donation(donation_id: int, ngo_name: str, ngo_contact: str = None, session: Session = Depends(get_session)):
    donation = session.get(models.Donation, donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.status.lower().startswith("claimed") or donation.status.lower() == "delivered":
        raise HTTPException(status_code=400, detail="Donation already claimed or delivered")
    donation.status = f"Claimed by {ngo_name}"
    # optional store contact
    if ngo_contact:
        donation.contact = ngo_contact
    session.add(donation)
    session.commit()
    session.refresh(donation)
    return {"message": f"Donation {donation_id} claimed by {ngo_name}", "donation": donation}

# --- Matching endpoint: match donor to nearest community/NGO need by food_type ---
class MatchRequest(models.SQLModel):
    donor_location: str
    food_type: str

@router.post("/matching")
def match_donor_ngo(req: MatchRequest, session: Session = Depends(get_session)):
    """
    Naive matching: find communities whose 'urgent_needs' text contains the food_type.
    Returns top matches (0..N).
    """
    communities = session.exec(select(models.Community)).all()
    matches = []
    ft = req.food_type.lower().strip()
    for c in communities:
        if c.urgent_needs and ft in c.urgent_needs.lower():
            matches.append({
                "community_id": c.id,
                "community_name": c.name,
                "location": c.location,
                "urgent_needs": c.urgent_needs
            })
    if not matches:
        raise HTTPException(status_code=404, detail="No matching communities/NGOs found")
    return {"donor_location": req.donor_location, "matches": matches}
