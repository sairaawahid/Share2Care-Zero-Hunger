from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel import Session
from app.backend.database import get_session
from app.backend import models

router = APIRouter(prefix="/api/communities", tags=["Communities"])

@router.post("/", response_model=models.Community)
def create_community(payload: models.Community, session: Session = Depends(get_session)):
    # payload may be SQLModel Community
    community = models.Community.from_orm(payload)
    session.add(community)
    session.commit()
    session.refresh(community)
    return community

@router.get("/", response_model=list[models.Community])
def list_communities(session: Session = Depends(get_session)):
    return session.exec(select(models.Community)).all()

@router.put("/{community_id}/urgent")
def mark_urgent(community_id: int, urgent: bool, session: Session = Depends(get_session)):
    community = session.get(models.Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    # store flag or urgent_needs field — keep a simple boolean field 'urgent_need' if present
    try:
        community.urgent_need = urgent
        session.add(community)
        session.commit()
        session.refresh(community)
    except Exception:
        # if model doesn't have urgent_need, set a text flag in urgent_needs
        if urgent:
            community.urgent_needs = (community.urgent_needs or "") + " ; URGENT"
        else:
            if community.urgent_needs:
                community.urgent_needs = community.urgent_needs.replace(" ; URGENT", "")
        session.add(community)
        session.commit()
        session.refresh(community)
    return {"message": "Community urgency updated", "community": community}
