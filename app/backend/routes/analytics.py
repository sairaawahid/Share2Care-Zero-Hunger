from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel import Session
from app.backend.database import get_session
from app.backend import models
from datetime import datetime, timedelta
import pandas as pd
import random

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/summary")
def analytics_summary(session: Session = Depends(get_session)):
    total_donations = session.exec(select(models.Donation)).count()
    total_communities = session.exec(select(models.Community)).count()
    total_deliveries = session.exec(select(models.Delivery)).count()
    delivered = session.exec(select(models.Delivery).where(models.Delivery.status == "delivered")).count()
    return {
        "total_donations": total_donations,
        "total_communities": total_communities,
        "total_deliveries": total_deliveries,
        "completed_deliveries": delivered
    }

@router.get("/forecasting/prices")
def forecasting_prices(days: int = 7):
    """
    Lightweight forecasting: synthesise simple historical series and return a smoothed forecast
    (avoids heavy dependencies). In production, replace with your prophet/pmdarima implementation.
    """
    today = datetime.utcnow().date()
    # create sample historical series (30 days) — replace with real WFP data if provided
    dates = pd.date_range(end=today, periods=30)
    values = [random.uniform(80, 150) for _ in range(len(dates))]
    df = pd.DataFrame({"ds": dates, "y": values})
    # rolling mean forecast
    mean = df["y"].rolling(7, min_periods=1).mean().iloc[-1]
    future = []
    for i in range(1, days + 1):
        future_date = today + timedelta(days=i)
        # simple random walk around mean
        future.append({
            "ds": future_date.isoformat(),
            "yhat": round(mean + random.uniform(-5, 5), 2),
            "yhat_lower": round(mean - 7 + random.uniform(-3, 3), 2),
            "yhat_upper": round(mean + 7 + random.uniform(-3, 3), 2)
        })
    return {"forecast": future}

@router.get("/severity")
def analytics_severity(session: Session = Depends(get_session)):
    """
    Aggregate community severity using community.urgent_needs or severity fields (if present).
    """
    comms = session.exec(select(models.Community)).all()
    if not comms:
        return {"message": "No community data"}
    # naive severity aggregation: count occurrences of keywords in urgent_needs
    high = 0
    medium = 0
    low = 0
    for c in comms:
        text = (c.urgent_needs or "").lower()
        if "severe" in text or "high" in text or "critical" in text:
            high += 1
        elif "moderate" in text or "medium" in text:
            medium += 1
        elif text:
            low += 1
    return {
        "total_communities": len(comms),
        "severity": {"high": high, "medium": medium, "low": low}
    }
