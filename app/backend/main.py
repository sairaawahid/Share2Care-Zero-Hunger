from fastapi import FastAPI
from app.backend.db import init_db
from app.backend.routes import (
    auth,
    donations,
    communities,
    delivery,
    analytics,
    psychology,
    admin,
)

app = FastAPI(
    title="Share2Care – Zero Hunger Backend",
    description="A full backend for connecting donors, NGOs, and communities to reduce food insecurity.",
    version="1.0.0",
)

# Startup Event
@app.on_event("startup")
def on_startup():
    init_db()

# Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Share2Care – Zero Hunger API"}

# Route Inclusions
app.include_router(auth.router)
app.include_router(donations.router)
app.include_router(communities.router)
app.include_router(delivery.router)
app.include_router(analytics.router)
app.include_router(psychology.router)
app.include_router(admin.router)
