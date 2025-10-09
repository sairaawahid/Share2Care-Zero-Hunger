from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel

#  User Models
class UserBase(SQLModel):
    name: str
    email: str
    role: Optional[str] = "donor"

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

class UserLogin(SQLModel):
    email: str
    password: str

# Donation Models
class DonationBase(SQLModel):
    title: str
    description: Optional[str] = None
    quantity: Optional[int] = 1
    category: Optional[str] = "Food"
    status: Optional[str] = "pending"
    donor_id: Optional[int] = None
    community_id: Optional[int] = None

class Donation(DonationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DonationCreate(DonationBase):
    pass

class DonationRead(DonationBase):
    id: int
    timestamp: datetime

# Community Models
class CommunityBase(SQLModel):
    name: str
    location: str
    population: Optional[int] = None
    urgent_needs: Optional[str] = None
    urgent_need: Optional[bool] = False

class Community(CommunityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CommunityCreate(CommunityBase):
    pass

class CommunityRead(CommunityBase):
    id: int

# Delivery Models
class DeliveryBase(SQLModel):
    donation_id: int
    driver_name: str
    vehicle_number: str
    delivery_status: Optional[str] = "scheduled"
    eta_minutes: Optional[int] = None
    completion_time: Optional[datetime] = None

class Delivery(DeliveryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryCreate(DeliveryBase):
    pass

class DeliveryRead(DeliveryBase):
    id: int
    assigned_at: datetime

# Analytics Models
class ForecastInput(SQLModel):
    days_ahead: int = 7
    category: Optional[str] = "Food"

class ForecastResult(SQLModel):
    date: datetime
    predicted_price: float

class ForecastResponse(SQLModel):
    category: str
    forecasts: List[ForecastResult]


# Psychology Models
class SentimentInput(SQLModel):
    text: str

class SentimentOutput(SQLModel):
    sentiment: str
    score: float

class NudgeInput(SQLModel):
    behavior: str

class NudgeOutput(SQLModel):
    message: str
    category: str

class MoodLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = None
    mood: str
    note: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MoodLogCreate(SQLModel):
    user_id: Optional[int] = None
    mood: str
    note: Optional[str] = None

class MoodLogRead(SQLModel):
    id: int
    user_id: Optional[int]
    mood: str
    note: Optional[str]
    timestamp: datetime

# Admin Models (Read-Only)
class AdminSummary(SQLModel):
    total_users: int
    total_donations: int
    total_communities: int
    total_deliveries: int
