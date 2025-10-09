## 🧩 Share2Care – Zero Hunger  
### Unified System Overview + Data Flow Diagram

```mermaid
flowchart TD
    %% ============================================================
    %% SHARE2CARE – ZERO HUNGER : UNIFIED SYSTEM OVERVIEW + DATA FLOW
    %% ============================================================

    %% === USERS LAYER ===
    subgraph U[👥 USER ROLES]
        U1[Donor\n• Register/Login\n• Add Surplus Food Donation\n• Track Deliveries]
        U2[NGO / Volunteer\n• View & Claim Donations\n• Deliver to Flood-Affected Communities]
        U3[Admin\n• Approve NGOs\n• View Analytics & AI Insights]
    end

    %% === FRONTEND LAYER ===
    subgraph F[🖥️ FRONTEND – Streamlit Web App]
        F1[Interactive UI Tabs\n1️⃣ Map\n2️⃣ Donor Dashboard\n3️⃣ NGO Dashboard\n4️⃣ Deliveries\n5️⃣ Analytics\n6️⃣ AI Insights\n7️⃣ Psychology\n8️⃣ Admin Panel]
        F2[API Integration Layer\n• Calls Backend Endpoints (FastAPI)\n• Handles Auth & Session State]
        F3[Real-Time Maps & Visuals\n• Geocoded Donations\n• Food Insecurity Heatmaps]
    end

    %% === BACKEND LAYER ===
    subgraph B[⚙️ BACKEND – FastAPI + SQLModel]
        direction TB
        B1[Auth Routes\n🔑 /api/auth → Register/Login]
        B2[Donations Routes\n🍛 /api/donations → Add/List Donations]
        B3[Communities Routes\n🏘️ /api/communities → View Needs, Mark Urgent]
        B4[Delivery Routes\n🚚 /api/delivery → Claim & Schedule]
        B5[Analytics Routes\n📈 /api/analytics → Food Price Trends & Forecasts]
        B6[Psychology Routes\n🧠 /api/psychology → Sentiment & Motivation]
        B7[Admin Routes\n⚙️ /api/admin → System Oversight]
        B8[Workflow Logic\n🔄 donor-ngo-workflow.py + services.py\n• Business rules linking donors ↔ NGOs ↔ deliveries]
    end

    %% === DATABASE LAYER ===
    subgraph D[🗄️ DATABASE – PostgreSQL (via SQLModel ORM)]
        D1[(users)]
        D2[(donations)]
        D3[(communities)]
        D4[(deliveries)]
        D5[(claims)]
        D6[(analytics_cache)]
    end

    %% === AI & ML LAYER ===
    subgraph M[🤖 AI + ML Modules]
        M1[DistilBERT\nSentiment & Motivation Analysis\n→ Psychology Route]
        M2[Prophet / ARIMA\nFood Price Forecasting\n→ Analytics Route]
        M3[MobileNetV2\nFood Image Tagging\n→ Donations Route]
        M4[GeoML Heatmaps\nFood Insecurity Mapping\n→ Map Visualization]
    end

    %% === STORAGE & FILE SYSTEM ===
    subgraph S[💾 Storage Layer]
        S1[PostgreSQL DB File / Cloud Volume]
        S2[donation_images/ Directory]
    end

    %% === DATA FLOW ===
    %% USER -> FRONTEND
    U1 -->|Adds Donation| F1
    U2 -->|Claims / Views| F1
    U3 -->|Monitors Data| F1

    %% FRONTEND -> BACKEND
    F2 -->|RESTful API Calls (JSON)| B
    F1 --> F2

    %% BACKEND ROUTING
    B1 --> D1
    B2 --> D2
    B3 --> D3
    B4 --> D4
    B5 --> D6
    B6 --> D1
    B7 --> D1
    B8 --> D2 & D4 & D5

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
    B2 -->|Upload/Serve Food Images| S2

    %% FRONTEND VISUAL OUTPUTS
    F3 -->|Displays AI + Analytics Insights| F1

    %% === STYLES ===
    classDef user fill:#ffecb3,stroke:#f57f17,stroke-width:1px;
    classDef frontend fill:#e3f2fd,stroke:#1565c0,stroke-width:1px;
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px;
    classDef db fill:#ede7f6,stroke:#4527a0,stroke-width:1px;
    classDef ai fill:#f3e5f5,stroke:#6a1b9a,stroke-width:1px;
    classDef storage fill:#f1f8e9,stroke:#689f38,stroke-width:1px;

    class U,U1,U2,U3 user
    class F,F1,F2,F3 frontend
    class B,B1,B2,B3,B4,B5,B6,B7,B8 backend
    class D,D1,D2,D3,D4,D5,D6 db
    class M,M1,M2,M3,M4 ai
    class S,S1,S2 storage
