from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.backend.models import Community
from app.backend.db import get_session

router = APIRouter()


@router.get("/communities")
def get_communities(session: Session = Depends(get_session)):
    communities = session.exec(select(Community)).all()
    return communities


@router.get("/communities/{community_id}")
def get_community(community_id: int, session: Session = Depends(get_session)):
    community = session.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return community


@router.get("/communities/{community_id}/needs")
def get_community_needs(community_id: int, session: Session = Depends(get_session)):
    community = session.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return {"urgent_needs": community.urgent_needs}

