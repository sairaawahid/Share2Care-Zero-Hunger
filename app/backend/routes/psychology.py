from fastapi import APIRouter
from transformers import pipeline
from pydantic import BaseModel

router = APIRouter(tags=["Psychology"])

sentiment_pipeline = pipeline("sentiment-analysis")

class SentimentInput(BaseModel):
    text: str

@router.post("/psychology/sentiment")
def analyze_sentiment(data: SentimentInput):
    """
    Analyzes donor or NGO sentiment using DistilBERT.
    """
    result = sentiment_pipeline(data.text)[0]
    label = result["label"]
    score = round(result["score"], 3)
    sentiment = "positive" if label == "POSITIVE" else "negative"
    return {"sentiment": sentiment, "confidence": score}
