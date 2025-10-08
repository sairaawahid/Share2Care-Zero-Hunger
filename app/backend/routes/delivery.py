from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel import Session
from app.backend.database import get_session
from app.backend import models
import random

router = APIRouter(prefix="/api/delivery", tags=["Delivery"])

@router.post("/")
def schedule_delivery(payload: models.Delivery, session: Session = Depends(get_session)):
    delivery = models.Delivery.from_orm(payload)
    session.add(delivery)
    session.commit()
    session.refresh(delivery)
    return {"message": "Delivery scheduled", "delivery": delivery}

@router.get("/")
def list_deliveries(session: Session = Depends(get_session)):
    return session.exec(select(models.Delivery)).all()

@router.put("/{delivery_id}/update-status")
def update_delivery_status(delivery_id: int, status: str, session: Session = Depends(get_session)):
    delivery = session.get(models.Delivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    delivery.status = status
    session.add(delivery)
    session.commit()
    session.refresh(delivery)
    return {"message": "Delivery status updated", "delivery": delivery}

@router.get("/routes")
def get_delivery_routes(session: Session = Depends(get_session)):
    """
    Returns an 'optimized' list of routes for scheduled deliveries.
    Since real routing requires external services, this returns simulated distances and sorted routes.
    """
    deliveries = session.exec(select(models.Delivery)).all()
    routes = []
    for d in deliveries:
        # attempt to fetch pickup/drop locations from donation/community if referenced
        try:
            donation = session.get(models.Donation, d.donor_id)
            pickup = donation.location if donation else "Unknown"
        except Exception:
            pickup = "Unknown"

        try:
            community = session.get(models.Community, d.community_id)
            drop = community.location if community else "Unknown"
        except Exception:
            drop = "Unknown"

        distance_km = round(random.uniform(2.0, 40.0), 2)
        routes.append({
            "delivery_id": d.id,
            "pickup": pickup,
            "drop": drop,
            "distance_km": distance_km,
            "status": d.status
        })

    routes.sort(key=lambda x: x["distance_km"])
    return {"routes": routes}
