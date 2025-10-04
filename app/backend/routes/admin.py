from fastapi import APIRouter, HTTPException
from database import users, donations, communities

router = APIRouter()

@router.get("/admin/users")
def list_users():
    return users

@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int):
    for u in users:
        if u.id == user_id:
            users.remove(u)
            return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/admin/donations")
def list_donations():
    return donations

@router.get("/admin/communities")
def list_communities():
    return communities