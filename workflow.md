## 🚀 Share2Care – App Workflow & Data Flow (Frontend-Focused)

```mermaid
flowchart TD
    %% ============================================================
    %% SHARE2CARE – FRONTEND + DATA FLOW DIAGRAM (Simplified)
    %% ============================================================

    %% === USERS ===
    subgraph U[User Roles]
        U1[👤 Donor]
        U2[🤝 NGO / Volunteer]
        U3[🛠️ Admin]
    end

    %% === FRONTEND ===
    subgraph F[🌐 Streamlit Frontend]
        F1[Home & Authentication]
        F2[Dashboard (Map, Donations, Analytics)]
        F3[Donation & Delivery Forms]
        F4[AI Insights & Visual Reports]
    end

    %% === BACKEND ===
    subgraph B[⚙️ FastAPI Backend]
        B1[(Auth API)]
        B2[(Donations API)]
        B3[(Delivery API)]
        B4[(Analytics API)]
        B5[(Psychology / AI Module)]
    end

    %% === DATABASE ===
    subgraph D[(🗄️ PostgreSQL Database)]
        D1[(Users)]
        D2[(Donations)]
        D3[(Deliveries)]
        D4[(Communities)]
        D5[(Mood Logs / Insights)]
    end

    %% === DATA FLOW ===
    %% Users → Frontend
    U1 -->|Register / Login| F1
    U1 -->|Add Donation| F3
    U2 -->|View & Claim Donations| F2
    U3 -->|View Reports & Analytics| F4

    %% Frontend → Backend
    F1 -->|POST /api/auth| B1
    F3 -->|POST /api/donations| B2
    F2 -->|GET /api/donations| B2
    F2 -->|POST /api/delivery| B3
    F4 -->|GET /api/analytics| B4
    F4 -->|GET /api/psychology| B5

    %% Backend → Database
    B1 --> D1
    B2 --> D2
    B3 --> D3
    B4 --> D2
    B4 --> D4
    B5 --> D5

    %% Database → Backend → Frontend → Users
    D -->|Returns Data via APIs| B
    B -->|JSON Responses| F
    F -->|Visualizes Data| U

sequenceDiagram
    participant Donor
    participant Frontend as Streamlit Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL Database
    participant NGO as NGO / Volunteer

    %% === 1. Donor Adds Donation ===
    Donor->>Frontend: Fill Donation Form
    Frontend->>API: POST /api/donations (JSON Payload)
    API->>DB: INSERT INTO Donations Table
    DB-->>API: ✅ Donation Saved
    API-->>Frontend: 201 Created (Donation ID)
    Frontend-->>Donor: Confirmation Message + Map Update
    API-->>NGO: 🔔 Notify Available Donation (via Dashboard Refresh)

    %% === 2. NGO Claims Donation ===
    NGO->>Frontend: Click “Claim” on Donation
    Frontend->>API: POST /api/delivery (claim_id, ngo_id)
    API->>DB: UPDATE donation.status = "Claimed"
    DB-->>API: ✅ Updated
    API-->>Frontend: 200 OK (Claim Confirmed)
    Frontend-->>NGO: Show “Delivery in Progress”
    API-->>Donor: 🔔 Notify Donation Claimed

    %% === 3. Delivery Completed ===
    NGO->>Frontend: Mark as Delivered
    Frontend->>API: PUT /api/delivery/{id} status="Delivered"
    API->>DB: UPDATE delivery.status = "Delivered"
    DB-->>API: ✅ Updated
    API-->>Frontend: 200 OK
    Frontend-->>Donor: Delivery Completed Notification

    %% === 4. Analytics & Insights ===
    Admin->>Frontend: View Dashboard
    Frontend->>API: GET /api/analytics
    API->>DB: SELECT * FROM donations, deliveries
    DB-->>API: Return Aggregated Data
    API-->>Frontend: JSON Data
    Frontend-->>Admin: 📊 Render Graphs, Trends & Maps
