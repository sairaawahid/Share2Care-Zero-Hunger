from fastapi import APIRouter, HTTPException
from models import Delivery
from database import deliveries

router = APIRouter()

def get_next_delivery_id():
    return len(deliveries) + 1

@router.post("/delivery")
def create_delivery(delivery: Delivery):
    delivery.id = get_next_delivery_id()
    deliveries.append(delivery)
    return {"message": "Delivery scheduled successfully", "delivery": delivery}

@router.get("/delivery/{delivery_id}")
def get_delivery(delivery_id: int):
    for d in deliveries:
        if d.id == delivery_id:
            return d
    raise HTTPException(status_code=404, detail="Delivery not found")

@router.put("/delivery/{delivery_id}/update-status")
def update_delivery_status(delivery_id: int, status: str):
    for d in deliveries:
        if d.id == delivery_id:
            d.status = status
            return {"message": "Status updated", "delivery": d}
    raise HTTPException(status_code=404, detail="Delivery not found")