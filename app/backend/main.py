# app/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.backend.routes import (
    auth,
    donations,
    communities,
    delivery,
    analytics,
    psychology,
    admin
)
from app.backend.database import init_db

app = FastAPI(title="Share2Care – Zero Hunger API")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Share2Care – Zero Hunger API"}

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include all route modules with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(donations.router, prefix="/api")
app.include_router(communities.router, prefix="/api")
app.include_router(delivery.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(psychology.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
