from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from fastapi import status, File, UploadFile

from src.models import Profile as ModelProfile
from src.schema import Profile as SchemaProfile
from PIL import Image
import os

profile = APIRouter()


@profile.get("/profiles", status_code=status.HTTP_200_OK)
def get_profile():
    db_profiles = db.session.query(ModelProfile).all()
    if not db_profiles:
        raise HTTPException(status_code=404, detail="Profiles not found")

    return db_profiles


@profile.get("/profiles/{profile_id}", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
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
    db_profile = ModelProfile(name=profile.name, email=profile.email, phone=profile.phone,
                              profile_photo_path='/', cover_photo_path='/', user_id=profile.user_id)

    db.session.add(db_profile)
    db.session.commit()
    return db_profile


@profile.post("/update-profile/{profile_id}", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def update_profile(profile_id: int, profile: SchemaProfile):
    db_profile = select_profile(profile_id)

    if (profile.name):
        db_profile.name = profile.name
    if (profile.email):
        db_profile.email = profile.email
    if (profile.phone):
        db_profile.phone = profile.phone
    if (profile.name):
        db_profile.user_id = profile.user_id

    db.session.commit()
    db.session.refresh(db_profile)
    return db_profile


@profile.delete("/delete-profile/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_profile(profile_id: int):
    db_profile = select_profile(profile_id)

    # await delete_photo(profile_id, 'profile')
    # await delete_photo(profile_id, 'cover')

    db.session.delete(db_profile)
    db.session.commit()
    return True


async def reduce_image_size(image_path):
    image_path = os.getcwd() + image_path
    image = Image.open(image_path)
    image.save(image_path, optimize=True, quality=70)


@profile.get("/profiles/photo/{type}/{profile_id}", status_code=status.HTTP_200_OK)
async def get_photo(profile_id, type):
    path = '/data_repository/profile/' + type + '/' + profile_id
    file = open(os.getcwd() + path, "rb")

    return file


@profile.post("/profiles/photo/{type}/{profile_id}", status_code=status.HTTP_200_OK)
async def add_photo(profile_id, type, image: UploadFile = File(...)):
    db_profile = select_profile(profile_id)

    filename = image.filename
    extension = filename.split(".")[-1]
    path = f'/profile/{type}/{profile_id}.{extension}'

    # Esto me permite actualizar y agregar en la misma
    if os.path.exists(path):
        delete_photo(profile_id, type)
    image_content = await image.read()

    os.makedirs(os.path.dirname(os.getcwd() + path), exist_ok=True)

    with open(os.getcwd() + path, "wb") as file:
        file.write(image_content)
    await reduce_image_size(path)
    file.close()

    if (type == 'profile'):
        db_profile.profile_photo_path = os.getcwd() + path
    if (type == 'cover'):
        db_profile.cover_photo_path = os.getcwd() + path

    db.session.commit()
    db.session.refresh(db_profile)
    return True


@profile.delete("/profiles/photo/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_photo(profile_id, type):
    path = '/data_repository/profile/' + type + '/' + profile_id

    path = os.getcwd() + path

    if os.path.exists(path):
        os.remove(path)
        return profile_id

    raise HTTPException(status_code=404, detail="File not found")
