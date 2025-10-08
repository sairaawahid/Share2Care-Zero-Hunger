from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    role: str = "donor"  # donor | ngo | admin
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Donation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    donor_id: int = Field(foreign_key="user.id")
    food_type: str
    quantity: float
    unit: str = "kg"
    location: str
    status: str = "pending"  # pending | claimed | delivered
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Community(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    location: str
    members: int
    need_level: float  # scale 0–100
    contact_person: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Delivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    donation_id: int = Field(foreign_key="donation.id")
    ngo_id: int = Field(foreign_key="user.id")
    route: str
    status: str = "scheduled"  # scheduled | in_transit | delivered
    scheduled_date: datetime = Field(default_factory=datetime.utcnow)

class SentimentLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    sentiment: str  # positive | neutral | negative
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    donor_id: int = Field(foreign_key="user.id")
    ngo_id: int = Field(foreign_key="user.id")
    donation_id: int = Field(foreign_key="donation.id")
    score: float
    matched_on: datetime = Field(default_factory=datetime.utcnow)
