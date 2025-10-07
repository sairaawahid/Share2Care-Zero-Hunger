# app/backend/models.py
from typing import Optional
from sqlmodel import SQLModel, Field

# ---------- Users ----------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    role: str = "donor"  # donor, volunteer, ngo, admin

class UserCreate(SQLModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "donor"

class UserLogin(SQLModel):
    email: str
    password: str

# ---------- Donations ----------
class Donation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    donor_id: Optional[int] = None
    food_type: str
    quantity: str
    location: str
    contact: Optional[str] = None
    image_path: Optional[str] = None
    status: str = "Available"

class DonationCreate(SQLModel):
    donor_id: Optional[int] = None
    food_type: str
    quantity: str
    location: str
    contact: Optional[str] = None
    image_path: Optional[str] = None

# ---------- Community ----------
class Community(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    population: int
    location: str
    urgent_needs: Optional[str] = None

# ---------- Delivery ----------
class Delivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    donor_id: Optional[int] = None
    community_id: Optional[int] = None
    status: str = "scheduled"  # scheduled, picked_up, delivered

# ---------- Psychology / misc ----------
class PsychologySurvey(SQLModel):
    user_id: int
    survey_data: dict
