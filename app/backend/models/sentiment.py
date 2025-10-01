from transformers import pipeline

# Explicitly pin the model + revision so no warnings appear in production
MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
MODEL_REVISION = "714eb0f"  # stable revision hash from Hugging Face

# Load once (cached in memory)
_sentiment = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    revision=MODEL_REVISION,
    device=-1   # force CPU (works on Streamlit Cloud)
)

def analyze_sentiment(text: str):
    """Return positive/neutral/negative score for a given text."""
    if not text or not text.strip():
        return {"label": "EMPTY", "score": 0.0}
    result = _sentiment(text[:512])[0]  # limit length
    return {"label": result["label"], "score": float(result["score"])}
