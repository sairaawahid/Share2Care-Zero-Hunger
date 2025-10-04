# routes/auth.py
from fastapi import APIRouter, HTTPException
from models import User, UserLogin
from database import users

router = APIRouter() 

# Mock auto-increment ID
def get_next_user_id():
    return len(users) + 1

@router.post("/register")
def register(user: User):
    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already exists")
    user.id = get_next_user_id()
    users.append(user)
    return {"message": "User registered successfully", "user": user}

@router.post("/login")
def login(user_login: UserLogin):
    for u in users:
        if u.email == user_login.email and u.password == user_login.password:
            return {"message": "Login successful", "user": u}
    raise HTTPException(status_code=401, detail="Invalid credentials")