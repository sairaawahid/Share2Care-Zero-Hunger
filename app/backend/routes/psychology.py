from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.backend.models import PsychologySurvey
from app.backend.db import get_session

router = APIRouter()


@router.post("/psychology/check-donor")
def check_donor_survey(survey: PsychologySurvey, session: Session = Depends(get_session)):
    # Placeholder for ML or behavioral model processing
    return {"message": "Donor psychological survey processed", "survey": survey.survey_data}


@router.post("/psychology/check-community")
def check_community_survey(survey: PsychologySurvey, session: Session = Depends(get_session)):
    # Placeholder for ML or behavioral model processing
    return {"message": "Community psychological survey processed", "survey": survey.survey_data}


@router.get("/psychology/recommendations")
def get_recommendations(user_id: int):
    return {"recommendations": f"Personalized recommendations for user {user_id}"}

