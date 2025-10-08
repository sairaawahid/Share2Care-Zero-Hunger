from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from app.backend.database import get_session
from app.backend import models

# prefer using your existing analyze_sentiment util if available
try:
    from app.backend.models.sentiment import analyze_sentiment as analyze_sentiment_util
except Exception:
    analyze_sentiment_util = None

router = APIRouter(prefix="/api/psychology", tags=["Psychology"])

class SentimentRequest(BaseModel):
    user_id: int | None = None
    text: str

@router.post("/sentiment")
def analyze_sentiment_endpoint(payload: SentimentRequest, session: Session = Depends(get_session)):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    if analyze_sentiment_util:
        res = analyze_sentiment_util(payload.text)
        label = res.get("label")
        score = res.get("score", 0.0)
    else:
        # fallback: simple polarity by counting positive/negative words
        text = payload.text.lower()
        pos_words = ["good", "great", "happy", "positive", "love", "hope"]
        neg_words = ["bad", "sad", "angry", "negative", "hate", "worry"]
        p = sum(1 for w in pos_words if w in text)
        n = sum(1 for w in neg_words if w in text)
        if p >= n and p > 0:
            label = "POSITIVE"
            score = min(0.99, 0.5 + 0.1 * p)
        elif n > p:
            label = "NEGATIVE"
            score = min(0.99, 0.5 + 0.1 * n)
        else:
            label = "NEUTRAL"
            score = 0.5

    # persist into sentiment logs table if present
    try:
        log = models.SentimentLog(user_id=payload.user_id or 0, mood=label, sentiment_score=score, note=payload.text)
        session.add(log)
        session.commit()
        session.refresh(log)
    except Exception:
        # non-fatal: model/table might not exist
        pass

    return {"label": label, "score": float(score)}
