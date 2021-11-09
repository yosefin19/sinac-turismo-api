import os

from PIL import Image
from fastapi import APIRouter, HTTPException, Depends
from fastapi import status, File, UploadFile
from fastapi_sqlalchemy import db

from src.authentication import auth_wrapper
from src.models import Profile as ModelProfile
from src.schema import Profile as SchemaProfile

profile = APIRouter()
# Extenciones validas para las imagenes disponibles a cargar
EXTENSIONS = ["png", "jpg", "jpeg"]


@profile.get("/profiles", status_code=status.HTTP_200_OK)
def get_profile():
    db_profiles = db.session.query(ModelProfile).all()
    if not db_profiles:
        raise HTTPException(status_code=404, detail="Profiles not found")

    return db_profiles


@profile.get("/profile", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_profile(profile_id=Depends(auth_wrapper)):
    profile = select_profile(profile_id)

    return profile


def select_profile_by_user_id(user_id):
    """
    Función para obtener el perfil de un usuario apartir del identificador.
    :param user_id: identificador de un usuario.
    :return db_profile: DAO de un perfil de usuario.
    :raise: HTTPException: no se encontro el perfil.
    """
    db_profile = db.session.query(ModelProfile).filter(ModelProfile.user_id == user_id).one()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile


def select_profile(profile_id: int):
    db_profile = db.session.query(ModelProfile).get(profile_id)

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return db_profile


@profile.post("/add-profile", response_model=SchemaProfile, status_code=status.HTTP_201_CREATED)
def add_profile(profile: SchemaProfile):
    db_profile = ModelProfile(name=profile.name, phone=profile.phone,
                              profile_photo_path='/', cover_photo_path='/', user_id=profile.user_id)

    db.session.add(db_profile)
    db.session.commit()
    return db_profile


@profile.post("/update-profile", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def update_profile(profile: SchemaProfile, profile_id=Depends(auth_wrapper)):
    db_profile = select_profile(profile_id)
    if (profile.name):
        db_profile.name = profile.name
    if (profile.phone):
        db_profile.phone = profile.phone
    if (profile.profile_photo_path):
        db_profile.profile_photo_path = profile.profile_photo_path
    if (profile.cover_photo_path):
        db_profile.cover_photo_path = profile.cover_photo_path

    db.session.commit()
    db.session.refresh(db_profile)
    return db_profile


@profile.delete("/delete-profile", status_code=status.HTTP_200_OK)
async def delete_profile(profile_id=Depends(auth_wrapper)):
    db_profile = select_profile(profile_id)

    await delete_photo(profile_id, 'profile')
    await delete_photo(profile_id, 'cover')

    db.session.delete(db_profile)
    db.session.commit()
    return True


async def reduce_image_size(image_path):
    image_path = os.getcwd() + image_path
    image = Image.open(image_path)
    image.save(image_path, optimize=True, quality=70)


@profile.get("/profiles/photo/{type}", status_code=status.HTTP_200_OK)
async def get_photo(type, profile_id=Depends(auth_wrapper)):
    directory_name = f'{type}'
    PATH = f'/data_repository/profile/{directory_name}/{profile_id}'

    path = PATH
    for ext in EXTENSIONS:
        pathE = path + '.' + ext
        if os.path.exists(pathE):
            file = open(pathE, "rb")
            return file
    raise HTTPException(status_code=404, detail="File not found")


@profile.post("/profiles/photo/{type}", status_code=status.HTTP_200_OK)
async def add_photo(type: str, image: UploadFile = File(...), profile_id=Depends(auth_wrapper)):
    db_profile = select_profile(profile_id)

    filename = image.filename
    extension = filename.split(".")[-1]

    # Esto me permite actualizar y agregar en la misma
    for ext in EXTENSIONS:
        pathExt = f'/data_repository/profile/{type}/{profile_id}.{ext}'
        if os.path.exists(pathExt):
            delete_photo(profile_id, type)

    path = f'/data_repository/profile/{type}/{profile_id}.{extension}'
    image_content = await image.read()

    os.makedirs(os.path.dirname(os.getcwd() + path), exist_ok=True)

    with open(os.getcwd() + path, "wb") as file:
        file.write(image_content)
    await reduce_image_size(path)
    file.close()

    if (type == 'profile'):
        db_profile.profile_photo_path = path
    if (type == 'cover'):
        db_profile.cover_photo_path = path

    db.session.commit()
    db.session.refresh(db_profile)
    return path


@profile.delete("/profiles/photo", status_code=status.HTTP_200_OK)
async def delete_photo(type, profile_id=Depends(auth_wrapper)):
    directory_name = f'{type}'
    PATH = f'/data_repository/profile/{directory_name}'
    db_profile = select_profile(profile_id)

    path = os.getcwd() + PATH

    for ext in EXTENSIONS:
        pathE = path + '.' + ext
        if os.path.exists(pathE):
            os.remove(pathE)
            if (type == 'profile'):
                db_profile.profile_photo_path = "/"
            if (type == 'cover'):
                db_profile.cover_photo_path = "/"

            db.session.commit()
            db.session.refresh(db_profile)
            return profile_id

    raise HTTPException(status_code=404, detail="File not found")


@profile.get("/users/all/auth-profiles/", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_authenticated_profile(user_id=Depends(auth_wrapper)):
    profiles = db.session.query(ModelProfile).filter(
        ModelProfile.user_id == user_id).all()
    if len(profiles) != 0:
        return profiles[0]

    raise HTTPException(status_code=404, detail="Profile not found")
