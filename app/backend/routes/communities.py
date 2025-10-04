from fastapi import APIRouter, HTTPException
from models import Community
from database import communities

router = APIRouter()

@router.get("/communities")
def get_communities():
    return communities

@router.get("/communities/{community_id}")
def get_community(community_id: int):
    for c in communities:
        if c.id == community_id:
            return c
    raise HTTPException(status_code=404, detail="Community not found")

@router.get("/communities/{community_id}/needs")
def get_community_needs(community_id: int):
    for c in communities:
        if c.id == community_id:
            return {"urgent_needs": c.urgent_needs}
    raise HTTPException(status_code=404, detail="Community not found")