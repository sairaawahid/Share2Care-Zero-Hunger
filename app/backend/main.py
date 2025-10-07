# app/backend/main.py
from fastapi import FastAPI
from routes import auth, donations, communities, delivery, analytics, psychology, admin
from app.backend.db import init_db

app = FastAPI(title="Share2Care – Zero Hunger Backend")

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include routers (same as before)
app.include_router(auth.router, prefix="/api")
app.include_router(donations.router, prefix="/api")
app.include_router(communities.router, prefix="/api")
app.include_router(delivery.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(psychology.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
