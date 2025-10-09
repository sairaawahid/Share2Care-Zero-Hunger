## 🧩 Share2Care – Zero Hunger  
### Unified System Overview and Data Flow Diagram

```mermaid
flowchart TD
    %% ============================================================
    %% SHARE2CARE – ZERO HUNGER : UNIFIED SYSTEM OVERVIEW + DATA FLOW
    %% ============================================================

    %% === USERS LAYER ===
    subgraph U[USER ROLES]
        U1[Donor: Register or Login; Add Surplus Food Donation; Track Deliveries]
        U2[NGO or Volunteer: View and Claim Donations; Deliver to Flood-Affected Communities]
        U3[Admin: Approve NGOs; View Analytics and AI Insights]
    end

    %% === FRONTEND LAYER ===
    subgraph F[FRONTEND – Streamlit Web App]
        F1[Interactive UI Tabs: Map; Donor Dashboard; NGO Dashboard; Deliveries; Analytics; AI Insights; Psychology; Admin Panel]
        F2[API Integration Layer: Calls Backend Endpoints via FastAPI; Handles Authentication and Session State]
        F3[Real-Time Maps and Visuals: Geocoded Donations; Food Insecurity Heatmaps]
    end

    %% === BACKEND LAYER ===
    subgraph B[BACKEND – FastAPI plus SQLModel]
        direction TB
        B1[Auth Routes: /api/auth → Register or Login]
        B2[Donations Routes: /api/donations → Add or List Donations]
        B3[Communities Routes: /api/communities → View Needs or Mark Urgent]
        B4[Delivery Routes: /api/delivery → Claim and Schedule]
        B5[Analytics Routes: /api/analytics → Food Price Trends and Forecasts]
        B6[Psychology Routes: /api/psychology → Sentiment and Motivation]
        B7[Admin Routes: /api/admin → System Oversight]
        B8[Workflow Logic: donor-ngo-workflow.py and services.py; Business rules linking donors, NGOs, and deliveries]
    end

    %% === DATABASE LAYER ===
    subgraph D[DATABASE – PostgreSQL via SQLModel ORM]
        D1[(users)]
        D2[(donations)]
        D3[(communities)]
        D4[(deliveries)]
        D5[(claims)]
        D6[(analytics_cache)]
    end

    %% === AI & ML LAYER ===
    subgraph M[AI and ML Modules]
        M1[DistilBERT: Sentiment and Motivation Analysis → Psychology Route]
        M2[Prophet or ARIMA: Food Price Forecasting → Analytics Route]
        M3[MobileNetV2: Food Image Tagging → Donations Route]
        M4[GeoML Heatmaps: Food Insecurity Mapping → Map Visualization]
    end

    %% === STORAGE & FILE SYSTEM ===
    subgraph S[STORAGE LAYER]
        S1[PostgreSQL Cloud Volume or Persistent Storage]
        S2[donation_images Directory]
    end

    %% === DATA FLOW ===
    %% USER -> FRONTEND
    U1 -->|Adds Donation| F1
    U2 -->|Claims or Views| F1
    U3 -->|Monitors Data| F1

    %% FRONTEND -> BACKEND
    F2 -->|RESTful API Calls returning JSON| B
    F1 --> F2

    %% BACKEND ROUTING
    B1 --> D1
    B2 --> D2
    B3 --> D3
    B4 --> D4
    B5 --> D6
    B6 --> D1
    B7 --> D1
    B8 --> D2
    B8 --> D4
    B8 --> D5

    %% BACKEND ↔ AI MODULES
    B2 --> M3
    B5 --> M2
    B6 --> M1
    B3 --> M4
    M1 --> F1
    M2 --> F1
    M3 --> F1
    M4 --> F3

    %% BACKEND ↔ DATABASE
    B -->|SQLModel ORM Queries| D
    D -->|Stores Persistent Data| S1

    %% BACKEND ↔ STORAGE
    B2 -->|Upload or Serve Food Images| S2

    %% FRONTEND VISUAL OUTPUTS
    F3 -->|Displays AI and Analytics Insights| F1

