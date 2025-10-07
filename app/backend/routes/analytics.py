from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.backend.models import Donation, Community, Delivery
from app.backend.db import get_session

router = APIRouter()


@router.get("/analytics/food-security")
def food_security_summary(session: Session = Depends(get_session)):
    total_donations = session.exec(select(func.count()).select_from(Donation)).one()
    total_communities = session.exec(select(func.count()).select_from(Community)).one()
    total_deliveries = session.exec(select(func.count()).select_from(Delivery)).one()

    return {
        "total_donations": total_donations,
        "total_communities": total_communities,
        "total_deliveries": total_deliveries
    }


@router.get("/analytics/trends")
def trends_summary(session: Session = Depends(get_session)):
    # Placeholder – you can later integrate real temporal trend analysis
    donations = session.exec(select(Donation)).all()
    deliveries = session.exec(select(Delivery)).all()

    return {
        "donations_over_time": len(donations),
        "deliveries_over_time": len(deliveries)
    }

