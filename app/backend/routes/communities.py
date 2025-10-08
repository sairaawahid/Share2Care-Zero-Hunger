from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from app.backend.database import get_session
from app.backend import models

router = APIRouter(prefix="/api/communities", tags=["Communities"])

@router.post("/", response_model=models.CommunityRead)
def create_community(payload: models.CommunityCreate, session: Session = Depends(get_session)):
    community = models.Community.from_orm(payload)
    session.add(community)
    session.commit()
    session.refresh(community)
    return community

@router.get("/", response_model=list[models.CommunityRead])
def list_communities(session: Session = Depends(get_session)):
    return session.exec(select(models.Community)).all()

@router.put("/{community_id}/urgent", response_model=models.CommunityRead)
def mark_urgent(community_id: int, urgent: bool, session: Session = Depends(get_session)):
    community = session.get(models.Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Try to use boolean urgent_need field; fall back to text if not available
    if hasattr(community, "urgent_need"):
        community.urgent_need = urgent
    else:
        if urgent:
            community.urgent_needs = (community.urgent_needs or "") + " ; URGENT"
        else:
            if community.urgent_needs:
                community.urgent_needs = community.urgent_needs.replace(" ; URGENT", "")

    session.add(community)
    session.commit()
    session.refresh(community)
    return community
