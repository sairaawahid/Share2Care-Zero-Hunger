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
    end

    %% === DATABASE ===
    subgraph D[(🗄️ PostgreSQL Database)]
        D1[(Users)]
        D2[(Donations)]
        D3[(Deliveries)]
        D4[(Communities)]
    end

    %% === BASIC DATA FLOW ===
    %% Users → Frontend
    U1 -->|Register / Login| F1
    U1 -->|Add Donation| F3
    U2 -->|View & Claim Donations| F2
    U3 -->|View Reports & Analytics| F4

    %% Frontend → Backend
    F1 -->|POST /api/auth| B1
    F3 -->|POST /api/donations| B2
    F2 -->|GET /api/donations| B2
    F2 -->|GET /api/delivery| B3
    F4 -->|GET /api/analytics| B4

    %% Backend → Database
    B1 --> D1
    B2 --> D2
    B3 --> D3
    B4 --> D2
    B4 --> D4

    %% Database → Backend → Frontend → Users
    D -->|Returns Data via APIs| B
    B -->|JSON Responses| F
    F -->|Visualizes Data| U

    %% === NOTES ===
    %% U = Users interact with Streamlit Frontend
    %% F = Frontend communicates with FastAPI via REST APIs
    %% B = Backend performs CRUD operations using SQLModel ORM
    %% D = Data is stored and retrieved from PostgreSQL
