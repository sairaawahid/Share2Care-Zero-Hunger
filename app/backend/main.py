# main.py
from fastapi import FastAPI
from routes import auth, donations, communities, delivery, analytics, psychology, admin

app = FastAPI(title="Share2Care – Zero Hunger Backend")

# Include all routers
app.include_router(auth.router, prefix="/api")
app.include_router(donations.router, prefix="/api")
app.include_router(communities.router, prefix="/api")
app.include_router(delivery.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(psychology.router, prefix="/api")
app.include_router(admin.router, prefix="/api")