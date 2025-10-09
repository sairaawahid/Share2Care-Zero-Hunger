## 🚀 Share2Care – App Workflow & Data Flow (Frontend-Focused)

### 🧩 High-Level Data Flow

```mermaid
flowchart TD
    %% === USERS ===
    subgraph U[User Roles]
        U1[Donor]
        U2[NGO / Volunteer]
        U3[Admin]
    end

    %% === FRONTEND ===
    subgraph F[Streamlit Frontend]
        F1[Home & Authentication]
        F2[Dashboard - Map, Donations, Analytics]
        F3[Donation & Delivery Forms]
        F4[AI Insights & Visual Reports]
    end

    %% === BACKEND ===
    subgraph B[FastAPI Backend]
        B1[Auth API]
        B2[Donations API]
        B3[Delivery API]
        B4[Analytics API]
        B5[Psychology / AI Module]
    end

    %% === DATABASE ===
    subgraph D[PostgreSQL Database]
        D1[Users Table]
        D2[Donations Table]
        D3[Deliveries Table]
        D4[Communities Table]
        D5[Mood Logs / Insights]
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
    D -->|Return Data via APIs| B
    B -->|JSON Responses| F
    F -->|Visualizes Data| U

