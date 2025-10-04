from fastapi import APIRouter
from database import donations, communities, deliveries

router = APIRouter()

@router.get("/analytics/food-security")
def food_security_summary():
    return {
        "total_donations": len(donations),
        "total_communities": len(communities),
        "total_deliveries": len(deliveries)
    }

@router.get("/analytics/trends")
def trends_summary():
    return {
        "donations_over_time": [len(donations)],  # Placeholder
        "deliveries_over_time": [len(deliveries)]
    }