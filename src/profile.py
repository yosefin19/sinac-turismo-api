from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from fastapi import status

from src.models import Profile as ModelProfile
from src.schema import Profile as SchemaProfile


profile = APIRouter()


@profile.get("/profiles", status_code=status.HTTP_200_OK)
def get_profile():
    db_profiles = db.session.query(ModelProfile).all()
    if not db_profiles:
        raise HTTPException(status_code=404, detail="Profiles not found")
    return db_profiles


@profile.get("/profiles/{profile_id}",response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_profile(profile_id: int):
    profile = select_profile(profile_id)
    return profile


def select_profile(profile_id: int):
    db_profile = db.session.query(ModelProfile).get(profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile


@profile.post("/add-profile", response_model=SchemaProfile, status_code=status.HTTP_201_CREATED)
def add_profile(profile: SchemaProfile):
    db_profile = ModelProfile(name = profile.name,email = profile.email, phone = profile.phone,
    admin = profile.admin, user_id = profile.user_id)

    db.session.add(db_profile)
    db.session.commit()
    return db_profile


@profile.post("/update-profile/{profile_id}",response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def update_profile(profile_id: int, profile: SchemaProfile, imagen):
    db_profile = select_profile(profile_id)
    
    if(profile.name):
        db_profile.name = profile.name
    if(profile.email):
        db_profile.email = profile.email
    if(profile.phone):
        db_profile.phone = profile.phone
    if(profile.admin):
        db_profile.admin = profile.admin
    if(profile.name):
        db_profile.user_id = profile.user_id

    db.session.commit()
    db.session.refresh(db_profile)
    return db_profile


@profile.delete("/delete-profile/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_profile(profile_id: int):
    db_profile = select_profile(profile_id)
    
    db.session.delete(db_profile)
    db.session.commit()
    return True 


