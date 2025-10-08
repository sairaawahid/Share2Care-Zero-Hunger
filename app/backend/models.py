# app/backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Donation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    donor_name: str
    food_item: str
    quantity: int
    status: str = "pending"

    deliveries: List["Delivery"] = Relationship(back_populates="donation")


class Community(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    location: str
    need_level: int
    received_donations: int = 0
    preferred_items: str = "general"

    deliveries: List["Delivery"] = Relationship(back_populates="community")


class Delivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    donation_id: int = Field(foreign_key="donation.id")
    community_id: int = Field(foreign_key="community.id")
    status: str = "scheduled"
    distance_km: float = 0.0

    donation: Optional[Donation] = Relationship(back_populates="deliveries")
    community: Optional[Community] = Relationship(back_populates="deliveries")
