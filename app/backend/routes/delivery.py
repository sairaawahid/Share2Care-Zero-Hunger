from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.backend.database import get_session
from app.backend.models import Delivery, Donation, Community

router = APIRouter(tags=["Delivery"])

@router.get("/delivery/routes")
def get_delivery_routes(session: Session = Depends(get_session)):
    """
    Returns delivery routes with donor and community details.
    """
    deliveries = session.exec(select(Delivery)).all()
    if not deliveries:
        raise HTTPException(status_code=404, detail="No delivery routes found.")

    routes = []
    for d in deliveries:
        donation = session.get(Donation, d.donation_id)
        community = session.get(Community, d.community_id)
        routes.append({
            "delivery_id": d.id,
            "donor": donation.donor_name if donation else None,
            "food_item": donation.food_item if donation else None,
            "destination": community.name if community else None,
            "status": d.status,
            "distance_km": d.distance_km,
        })
    return {"routes": routes}
