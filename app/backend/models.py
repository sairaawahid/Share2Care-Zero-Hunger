from pydantic import BaseModel
from typing import Optional

# User
class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    role: str  # donor, volunteer, admin

class UserLogin(BaseModel):
    email: str
    password: str

# Donation
class Donation(BaseModel):
    id: int
    donor_id: int
    food_type: str
    quantity: int
    location: str

# Community
class Community(BaseModel):
    id: int
    name: str
    population: int
    location: str
    urgent_needs: Optional[str] = None

# Delivery
class Delivery(BaseModel):
    id: int
    donor_id: int
    community_id: int
    status: str  # scheduled, picked_up, delivered

# Psychology
class PsychologySurvey(BaseModel):
    user_id: int
    survey_data: dict