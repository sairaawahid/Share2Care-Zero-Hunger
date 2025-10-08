from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.backend.database import get_session
from app.backend.models import Donation, Community
from prophet import Prophet
import pandas as pd

router = APIRouter(tags=["Analytics"])

@router.get("/analytics/severity")
def get_food_need_severity(session: Session = Depends(get_session)):
    """
    Returns food need severity per community based on unmet donations.
    """
    communities = session.exec(select(Community)).all()
    if not communities:
        raise HTTPException(status_code=404, detail="No communities found.")

    data = []
    for c in communities:
        need_gap = max(c.need_level - c.received_donations, 0)
        severity = min(round(need_gap / max(c.need_level, 1), 2), 1.0)
        data.append({
            "community": c.name,
            "location": c.location,
            "need_level": c.need_level,
            "received_donations": c.received_donations,
            "severity": severity
        })

    return {"severity_index": data}


@router.get("/forecasting/prices")
def forecast_food_prices():
    """
    Uses Prophet to forecast food price trends for the next 30 days.
    """
    # Simulated historical price data (you can replace with actual)
    df = pd.DataFrame({
        "ds": pd.date_range(start="2024-01-01", periods=120),
        "y": [100 + i*0.2 + (i % 7)*2 for i in range(120)]
    })

    model = Prophet(daily_seasonality=True)
    model.fit(df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    return {
        "forecast": forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(30).to_dict(orient="records")
    }


@router.post("/donor-matching/match")
def donor_community_match(session: Session = Depends(get_session)):
    """
    Suggests matches between donors and communities based on food need levels.
    """
    donations = session.exec(select(Donation)).all()
    communities = session.exec(select(Community)).all()
    if not donations or not communities:
        raise HTTPException(status_code=404, detail="Insufficient data for matching.")

    matches = []
    for donation in donations:
        best_match = min(
            communities,
            key=lambda c: abs(c.need_level - donation.quantity)
        )
        matches.append({
            "donor": donation.donor_name,
            "food_item": donation.food_item,
            "quantity": donation.quantity,
            "matched_community": best_match.name,
            "community_need_level": best_match.need_level
        })

    return {"matches": matches}
