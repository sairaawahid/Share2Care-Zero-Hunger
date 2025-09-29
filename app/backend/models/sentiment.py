from transformers import pipeline

# small, fast default (English)
_sentiment = pipeline("sentiment-analysis")

def analyze_text(text: str):
    if not text or not text.strip():
        return {"label":"NEUTRAL","score":0.0}
    res = _sentiment(text[:512])[0]
    return {"label": res["label"], "score": float(res["score"])}
