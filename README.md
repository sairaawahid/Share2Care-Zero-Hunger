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

## Hackathon
GNEC Hackathon 2025 Fall — SDG 2 (Zero Hunger)
