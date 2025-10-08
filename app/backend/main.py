from fastapi import FastAPI
from app.backend.database import init_db
from app.backend.routes import (
    auth,
    donations,
    communities,
    delivery,
    analytics,
    psychology,
    admin,
)

app = FastAPI(title="Share2Care – Zero Hunger Backend")

# Initialize DB tables on startup
@app.on_event("startup")
def on_startup():
    # models must already be importable; init_db uses SQLModel metadata
    init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to Share2Care – Zero Hunger API"}

# Include routers under /api prefix
app.include_router(auth.router)
app.include_router(donations.router)
app.include_router(communities.router)
app.include_router(delivery.router)
app.include_router(analytics.router)
app.include_router(psychology.router)
app.include_router(admin.router)
