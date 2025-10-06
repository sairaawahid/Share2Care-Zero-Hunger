# Share2Care – Zero Hunger

A lightweight, data-driven web app for Pakistan that:
- Maps food-security needs (OCHA FSC + admin boundaries)
- Enables surplus-food listings and claims
- Adds a psychology layer (nudges, pledges, mood reflections)
- **Optional AI**: food-image auto-tagging (MobileNet) + WFP food-price forecasting (Prophet/ARIMA/LSTM)

## Tech
Streamlit · (FastAPI optional) · Postgres/Supabase or SQLite · Folium/Leaflet · Transformers · Torch · Prophet/pmdarima

## Folders
- `app/backend/` — APIs, data loaders, forecasting
- `app/frontend/` — Streamlit UI
- `app/data/` — raw/processed datasets (keep big files out of Git)
- `app/models/` — lightweight models or metadata
- `notebooks/` — exploration & preprocessing

## Repo Structure
```bash
app/
 ├── backend/
 │    ├── main.py                  ← FastAPI entry point
 │    ├── config.py                ← Paths to data/models
 │    ├── data_loader.py           ← Data preprocessing utilities
 │    ├── donor-ngo-workflow.py    ← Donation workflow (DB + logic)
 │    ├── database.py              ← Mock in-memory DB
 │    ├── models/                  ← Pydantic models for request/response validation
 │    │     ├── image_tagging.py   ← Food image classification (MobileNet)
 │    │     ├── sentiment.py       ← Sentiment analysis pipeline
 │    │     ├── price_forecast.py  ← Forecasting food prices (Prophet/ARIMA)
 │    ├── data/
 │    │     ├── init_donations_csv.py
 │    ├── routes/                  ← API endpoints
 │    │     ├── auth.py            ← Login/register endpoints
 │    │     ├── donations.py       ← Donations CRUD
 │    │     ├── communities.py     ← Communities info
 │    │     ├── delivery.py        ← Delivery scheduling
 │    │     ├── analytics.py       ← Data visualization endpoints
 │    │     ├── psychology.py      ← Psychological features
 │    │     ├── admin.py           ← Admin endpoints
 │    ├── requirements.txt         ← Dependencies
 ├── frontend/                     ← Streamlit or React front-end
 ├── data/                         ← raw/processed datasets
 ├── models/                       ← ML models
 └── scripts/
      ├── prepare_core.py
      ├── check_wfp.py
```
## Hackathon
GNEC Hackathon 2025 Fall — SDG 2 (Zero Hunger)
