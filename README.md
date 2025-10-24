# Share2Care – Zero Hunger

### A Smart Food Redistribution Platform  
**Connecting surplus food donors with flood-affected communities across Pakistan** — powered by AI-driven insights to promote **UN SDG 2: Zero Hunger**.

Share2Care – Zero Hunger is a lightweight humanitarian web application designed to connect surplus food donors with flood-affected or food-insecure communities in Pakistan, while integrating AI-driven analytics, psychological support and real-time food security visualization.

The app visualizes real-time food needs and donation availability using interactive maps and dashboards and integrates psychological features to promote empathy, volunteer motivation and emotional well-being.

---

## Project Overview

**Share2Care – Zero Hunger** bridges the gap between *food surplus* and *scarcity* through an integrated platform where donors, NGOs and volunteers collaborate to deliver food efficiently and responsibly.

Floods and disasters cause severe disruptions to food supply chains, leaving many without access to meals, while surplus food often goes wasted elsewhere. In flood-affected regions of Pakistan, food wastage coexists with severe hunger and logistical inefficiencies. Donors often have surplus food, but NGOs and local communities lack visibility and real-time coordination tools to allocate resources efficiently.

**Current gap:**
-	No centralized, user-friendly platform connects **donors**, **volunteers**, and **recipients** efficiently.
-	Manual coordination leads to delays, duplication, and food spoilage.
-	Psychological strain among both victims and volunteers often goes unaddressed.

Share2Care solves these problems by:
-	Enabling **real-time matching** of donors and recipients based on **location and food availability**.
-	Providing **AI-driven analytics** to optimize routes and reduce waste.
-	Offering **psychological well-being modules** (e.g., motivation, gratitude tracking, empathy prompts) for community health.


---

## Objectives

| Goal | Description |
|------|--------------|
| **Reduce Food Waste** | Redirect surplus food from donors to flood-affected and food-insecure communities. |
| **Empower Local NGOs** | Enable NGOs to view, claim, and manage donations efficiently through real-time dashboards. |
| **Promote Sustainable Giving** | Use AI-driven nudges to encourage consistent donor behavior. |
| **Enhance Transparency** | Track every donation from pickup to delivery, ensuring accountability and impact visibility. |
| **Leverage AI for Impact** | Apply ML models for sentiment, forecasting, and food recognition to optimize logistics and community engagement. |

---

## Key Features

- **Donation Management** – Add, view, and claim surplus food donations.  
- **Community Mapping** – Real-time visualization of donation hotspots and NGO coverage.  
- **Delivery Tracking** – End-to-end monitoring from pickup to recipient.  
- **AI-Powered Modules:**  
  - *DistilBERT Sentiment Analysis* – Understand user emotions and satisfaction.  
  - *Prophet/ARIMA Forecasting* – Predict food price trends and resource needs.  
  - *MobileNetV2 Food Recognition* – Automatically identify food items from images.  
  - *Behavioral Nudges* – Motivate consistent donor participation.  
- **Mood Tracking** – Log donor/volunteer moods for mental well-being analysis.  
- **Impact Analytics** – Monitor metrics like total food saved, communities served, and donor engagement.

---

## Tech Stack

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
## Attribution
Share2Care was collaboratively developed by:
- [Sairaaw](https://www.linkedin.com/in/sairaabdulwahid/) (Backend Development, AI/ML Engineering)

We built this together to reduce hunger, encourage sustainability and demonstrate how technology can empower humanity.✨

If you use or adapt this app, please credit the developer(s) by linking to the original GitHub repository:
🔗 [https://github.com/sairaawahid/SentiMuse](https://github.com/sairaawahid/Share2Care-Zero-Hunger)

---
If you liked this project or want to collaborate on emotion-first AI tools, reach out via LinkedIn or GitHub:

**Sairaaw →** [LinkedIn](https://www.linkedin.com/in/sairaabdulwahid/) or [GitHub](https://github.com/sairaawahid)

---

This project was developed for the **GNEC Hackathon 2025 (Fall)** under the **SDG 2: Zero Hunger** theme.
