from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.backend.models import Delivery
from app.backend.db import get_session

router = APIRouter()


@router.post("/delivery")
def create_delivery(delivery: Delivery, session: Session = Depends(get_session)):
    session.add(delivery)
    session.commit()
    session.refresh(delivery)
    return {"message": "Delivery scheduled successfully", "delivery": delivery}


@router.get("/delivery/{delivery_id}")
def get_delivery(delivery_id: int, session: Session = Depends(get_session)):
    delivery = session.get(Delivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.put("/delivery/{delivery_id}/update-status")
def update_delivery_status(delivery_id: int, status: str, session: Session = Depends(get_session)):
    delivery = session.get(Delivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    delivery.status = status
    session.add(delivery)
    session.commit()
    session.refresh(delivery)
    return {"message": "Status updated", "delivery": delivery}

