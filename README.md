# Share2Care – Zero Hunger

### A Smart Food Redistribution Platform  
**Connecting surplus food donors with flood-affected communities across Pakistan** — powered by AI-driven insights to promote **UN SDG 2: Zero Hunger**.

---

## 🎯 1. Objectives

| Goal | Description |
|------|--------------|
| **Reduce Food Waste** | Redirect surplus food from donors to flood-affected and food-insecure communities. |
| **Empower Local NGOs** | Enable NGOs to view, claim, and manage donations efficiently through real-time dashboards. |
| **Promote Sustainable Giving** | Use AI-driven nudges to encourage consistent donor behavior. |
| **Enhance Transparency** | Track every donation from pickup to delivery, ensuring accountability and impact visibility. |
| **Leverage AI for Impact** | Apply ML models for sentiment, forecasting, and food recognition to optimize logistics and community engagement. |

---

## 🌐 2. Project Overview

**Share2Care – Zero Hunger** bridges the gap between *food surplus* and *scarcity* through an integrated platform where donors, NGOs, and volunteers collaborate to deliver food efficiently and responsibly.

This project was developed for the **GNEC Hackathon 2025 (Fall)** under the **SDG 2: Zero Hunger** theme.

---

## ✨ 3. Key Features

- 🥫 **Donation Management** – Add, view, and claim surplus food donations.  
- 🗺️ **Community Mapping** – Real-time visualization of donation hotspots and NGO coverage.  
- 🚚 **Delivery Tracking** – End-to-end monitoring from pickup to recipient.  
- 🤖 **AI-Powered Modules:**  
  - *DistilBERT Sentiment Analysis* – Understand user emotions and satisfaction.  
  - *Prophet/ARIMA Forecasting* – Predict food price trends and resource needs.  
  - *MobileNetV2 Food Recognition* – Automatically identify food items from images.  
  - *Behavioral Nudges* – Motivate consistent donor participation.  
- 💬 **Mood Tracking** – Log donor/volunteer moods for mental well-being analysis.  
- 📊 **Impact Analytics** – Monitor metrics like total food saved, communities served, and donor engagement.

---


---

## 🧰 5. Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | FastAPI, SQLite / PostgreSQL |
| **Frontend** | Streamlit |
| **AI/ML Models** | DistilBERT, Prophet, ARIMA, MobileNetV2 |
| **Visualization** | Folium, Plotly |
| **Authentication** | JWT |
| **Environment** | Python 3.11, Uvicorn, SQLAlchemy, Pydantic |

---

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
---

If you liked this project or want to collaborate on emotion-first AI tools, reach out via LinkedIn or GitHub:

**Sairaaw →** [LinkedIn](https://www.linkedin.com/in/sairaabdulwahid/) or [GitHub](https://github.com/sairaawahid)

---

Developed with the purpose of reducing hunger, encouraging sustainability and demonstrating how technology can empower humanity at the GNEC Hackathon 2025 Fall.
