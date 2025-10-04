from fastapi import APIRouter
from models import PsychologySurvey
from database import users

router = APIRouter()

@router.post("/psychology/check-donor")
def check_donor_survey(survey: PsychologySurvey):
    return {"message": "Donor psychological survey processed", "survey": survey.survey_data}

@router.post("/psychology/check-community")
def check_community_survey(survey: PsychologySurvey):
    return {"message": "Community psychological survey processed", "survey": survey.survey_data}

@router.get("/psychology/recommendations")
def get_recommendations(user_id: int):
    return {"recommendations": f"Personalized recommendations for user {user_id}"}
