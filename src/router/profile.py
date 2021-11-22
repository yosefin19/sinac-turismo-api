import os
from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from fastapi import status, File, UploadFile
from fastapi_sqlalchemy import db

from src.authentication import auth_wrapper
from src.models import FavoriteDestination, Profile as ModelProfile
from src.repository import EXTENSIONS, reduce_image_size
from src.router.tourist_destination import *
import src.router.user as user
from src.schema import Profile as SchemaProfile

profile = APIRouter()


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
    """
    Función para obtener los datos de un usuario de la base de datos.
    :param profile_id: identificador del perfil del usuario
    :return: DTO con los datos del perfil
    """
    db_profile = db.session.query(ModelProfile).get(profile_id)

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return db_profile


@profile.get("/profiles", status_code=status.HTTP_200_OK)
def get_profiles(admin_id=Depends(auth_wrapper)):
    """
    Función para obtener los datos de todos los perfiles registrados.
    :param admin_id: credenciales de ususario administrador.
    :return: Lista con todos los datos de los perfiles.
    :raise Error 401: No tiene permisos.
    """
    db_user = user.select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')
    db_profiles = db.session.query(ModelProfile).all()

    return db_profiles


@profile.get("/profile", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_profile(profile_id=Depends(auth_wrapper)):
    """
    Ruta para obtener el perfil de un usuario.
    :param profile_id: identificador del perfil.
    :return: DTO con los datos del perfil.
    """
    db_profile = select_profile(profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return db_profile


@profile.get("/profile/{profile_id}", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_profile_by_id(profile_id: int, admin_id=Depends(auth_wrapper)):
    """
    Ruta para obtener el perfil de un usuario.
    :param profile_id: identificador del perfil.
    :param admin_id: token asociado a un usuario administrador
    :return: DTO con los datos del perfil.
    :raise Error 401: No tiene permisos.
    :raise Error 404: el perfil no se encontro
    """
    db_user = user.select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    db_profile = select_profile(profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return db_profile


@profile.post("/add-profile", response_model=SchemaProfile, status_code=status.HTTP_201_CREATED)
def add_profile(profile_schema: SchemaProfile):
    """
    Ruta para registrar un nuevo perfil en la base de datos.
    :param profile_schema: datos del perfil ha registrar.
    :return: DTO con los datos del nuevo perfil
    """
    try:
        db_profile = ModelProfile(name=profile_schema.name, phone=profile_schema.phone,
                                  profile_photo_path='/', cover_photo_path='/', user_id=profile_schema.user_id)

        db.session.add(db_profile)
        db.session.commit()
        return db_profile
    except:
        raise HTTPException(status_code=404, detail="User not exists")


def update_profile(profile_schema: SchemaProfile, profile_id: int):
    """
    Función para actualizar los datos de un perfil de la base de datos.
    :param profile_schema: datos a actualizar del perfil
    :param profile_id: identificador del pefil.
    :return: DTO del perfil actualizado
    """
    db_profile = select_profile(profile_id)
    if profile_schema.name:
        db_profile.name = profile_schema.name
    if profile_schema.phone:
        db_profile.phone = profile_schema.phone
    if profile_schema.profile_photo_path:
        db_profile.profile_photo_path = profile_schema.profile_photo_path
    if profile_schema.cover_photo_path:
        db_profile.cover_photo_path = profile_schema.cover_photo_path

    db.session.commit()
    db.session.refresh(db_profile)
    return db_profile


@profile.post("/update-profile", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def update_personal_profile(profile_schema: SchemaProfile, profile_id=Depends(auth_wrapper)):
    """
    Ruta para que un usuario pueda modificar su propio perfil.
    :param profile_schema: datos del perfil ha actualizar.
    :param profile_id: indentificador del perfil del usuario.
    :return: datos del pefil actualizado
    """
    return update_profile(profile_schema, profile_id)


@profile.post("/update-profile/{profile_id}", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def update_profile_by_id(profile_id: int, profile_schema: SchemaProfile, admin_id=Depends(auth_wrapper)):
    """
    Ruta para que un usuario pueda modificar su propio perfil.
    :param profile_schema: datos del perfil ha actualizar.
    :param profile_id: indentificador del perfil del usuario.
    :param admin_id: credenciales de un usuario administrador.
    :return: datos del pefil actualizado
    """

    db_user = user.select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return update_profile(profile_schema, profile_id)


async def delete_profile(profile_id: int):
    db_profile = select_profile(profile_id)

    await delete_photo('profile', profile_id)
    await delete_photo( 'cover', profile_id)

    db.session.delete(db_profile)
    db.session.commit()
    return True


@profile.delete("/delete-profile", status_code=status.HTTP_200_OK)
async def delete_personal_profile(profile_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para que los usuarios eliminen sus propios perfiles.
    :param profile_id: identificador del perfil.
    :return: Verdadero si se elimino correctamente
    """
    return await delete_profile(profile_id)


@profile.delete("/delete-profile/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_profile_by_id(profile_id: int, admin_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para eliminen un perfil perfiles.
    :param profile_id: identificador del perfil.
    :param admin_id: credenciales de un usuario administrador.
    :return: Verdadero si se elimino correctamente
    """
    db_user = user.select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return await delete_profile(profile_id)


@profile.get("/profiles/photo/{type}", status_code=status.HTTP_200_OK)
async def get_photo(type, profile_id=Depends(auth_wrapper)):
    """
    Ruta para obtener las fotografías de perfil o portada de un usuario.
    :param type: tipo de fotografia, puede ser profile o cover.
    :param profile_id: identificador del perfil al que estan asociadas las imagenes.
    :return: los datos del archivo.
    :raise Error 404: no se encontro el archivo.
    """
    directory_name = f'{type}'
    PATH = f'/data_repository/profile/{directory_name}/{profile_id}'

    path = PATH
    for ext in EXTENSIONS:
        pathE = path + '.' + ext
        if os.path.exists(pathE):
            file = open(pathE, "rb")
            return file
    raise HTTPException(status_code=404, detail="File not found")


async def add_photo(type, image, profile_id):
    """
    Función para guardar una fotografia de perfil o portada de un usuario.
    :param type:
    :param image:
    :param profile_id:
    :return: ruta de la imagen.
    """
    db_profile = select_profile(profile_id)

    filename = image.filename
    extension = filename.split(".")[-1]

    # Esto me permite actualizar y agregar en la misma
    for ext in EXTENSIONS:
        pathExt = f'/data_repository/profile/{type}/{profile_id}.{ext}'
        if os.path.exists(pathExt):
            await delete_photo(profile_id, type)

    path = f'/data_repository/profile/{type}/{profile_id}.{extension}'
    image_content = await image.read()

    os.makedirs(os.path.dirname(os.getcwd() + path), exist_ok=True)

    with open(os.getcwd() + path, "wb") as file:
        file.write(image_content)
    await reduce_image_size(path)
    file.close()

    if type == 'profile':
        db_profile.profile_photo_path = path
    if type == 'cover':
        db_profile.cover_photo_path = path

    db.session.commit()
    db.session.refresh(db_profile)
    return path


@profile.post("/profiles/photo/{type}", status_code=status.HTTP_200_OK)
async def add_personal_photo(type: str, image: UploadFile = File(...), profile_id=Depends(auth_wrapper)):
    """
    Ruta para que el usuario agrege las fotogracias de perfil y portada de un usuario.
    :param type: tipo de fotografia, puede ser profile o cover.
    :param profile_id: identificador del perfil al que estan asociadas las imagenes.
    :param image: imagen a registrar.
    :return: ruta de la imagen
    """
    return await add_photo(type, image, profile_id)


@profile.post("/profiles/photo/{type}/{profile_id}", status_code=status.HTTP_200_OK)
async def add_photo_by_id(profile_id: int, type: str, image: UploadFile = File(...), admin_id=Depends(auth_wrapper)):
    """
    Ruta para agregar las fotogracias de perfil y portada de un usuario.
    :param type: tipo de fotografia, puede ser profile o cover.
    :param profile_id: identificador del perfil al que estan asociadas las imagenes.
    :param admin_id: credenciales de un usuario administrador.
    :param image: imagen a registrar.
    :return: ruta de la imagen
    """
    db_user = user.select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return await add_photo(type, image, profile_id)


async def delete_photo(type, profile_id):
    """
    Función para eliminar fotografías de los usuarios del sistema de archivos.
    :param type: tipo de fotografia, puede ser profile o cover.
    :param profile_id: identificador del perfil al que estan asociadas las imagenes.
    :return: profile_id
    """
    directory_name = f'{type}'
    PATH = f'/data_repository/profile/{directory_name}/{profile_id}'
    db_profile = select_profile(profile_id)

    path = os.getcwd() + PATH

    for ext in EXTENSIONS:
        pathE = path + '.' + ext
        if os.path.exists(pathE):
            os.remove(pathE)
            if type == 'profile':
                db_profile.profile_photo_path = "/"
            if type == 'cover':
                db_profile.cover_photo_path = "/"

            db.session.commit()
            db.session.refresh(db_profile)
            return profile_id

    raise HTTPException(status_code=404, detail="File not found")


@profile.delete("/profiles/photo/{type}", status_code=status.HTTP_200_OK)
async def delete_personal_photo(type, profile_id=Depends(auth_wrapper)):
    """
     Función para eliminar fotografías de los usuarios del sistema de archivos.
     :param type: tipo de fotografia, puede ser profile o cover.
     :param profile_id: identificador del perfil al que estan asociadas las imagenes.
     :return: profile_id
     """
    return await delete_photo(type, profile_id)


@profile.delete("/profiles/photo/{type}/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_photo_by_id(profile_id: int, type, admin_id=Depends(auth_wrapper)):
    """
     Función para eliminar fotografías de los usuarios del sistema de archivos.
     :param type: tipo de fotografia, puede ser profile o cover.
     :param profile_id: identificador del perfil al que estan asociadas las imagenes.
     :param admin_id: credenciales de un usuario administrador.
     :return: profile_id
     """
    db_user = user.select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return await delete_photo(type, profile_id)


@profile.get("/users/{user_id}/profiles/", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_profile_by_user(user_id: int):
    favorite_areas = db.session.query(ModelProfile).filter(
        ModelProfile.user_id == user_id).all()
    if len(favorite_areas) != 0:
        return favorite_areas[0]

    raise HTTPException(status_code=404, detail="Profile not found")


@profile.get("/users/all/auth-profiles/", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_authenticated_profile(user_id=Depends(auth_wrapper)):
    profiles = db.session.query(ModelProfile).filter(
        ModelProfile.user_id == user_id).all()
    if len(profiles) != 0:
        return profiles[0]

    raise HTTPException(status_code=404, detail="Profile not found")


@profile.get("/users/all/auth-profiles/", response_model=SchemaProfile, status_code=status.HTTP_200_OK)
def get_authenticated_profile(user_id=Depends(auth_wrapper)):
    """
    Ruta para obtener el perfil del usuario autentificado con sus credenciales.
    :param user_id: credenciales del usuario.
    :return: DTO del perfil del usuario
    """
    profiles = db.session.query(ModelProfile).filter(
        ModelProfile.user_id == user_id).all()
    if len(profiles) != 0:
        return profiles[0]

    raise HTTPException(status_code=404, detail="Profile not found")


@profile.get("/profile/recommendation/")
async def recommendation(user_id=Depends(auth_wrapper)):
    """
    Ruta que se encarga de generar los destinos favoritos de un usuario.
    :param user_id: credenciales del usuario
    :return: lista de destinos recomendados
    """
    favorite = db.session.query(ModelTouristDestination).join(FavoriteDestination). \
        filter(FavoriteDestination.user_id == user_id).all()
    if favorite:
        beach = len(db.session.query(ModelTouristDestination).join(FavoriteDestination). \
                    filter(FavoriteDestination.user_id == user_id, ModelTouristDestination.is_beach == True).all())
        volcano = len(db.session.query(ModelTouristDestination).join(FavoriteDestination). \
                      filter(FavoriteDestination.user_id == user_id, ModelTouristDestination.is_volcano == True).all())
        forest = len(db.session.query(ModelTouristDestination).join(FavoriteDestination). \
                     filter(FavoriteDestination.user_id == user_id, ModelTouristDestination.is_forest == True).all())
        mountain = len(db.session.query(ModelTouristDestination).join(FavoriteDestination). \
                       filter(FavoriteDestination.user_id == user_id,
                              ModelTouristDestination.is_mountain == True).all())
        maxi = max(beach, volcano, forest, mountain)

        tourist_destinations = []
        if maxi == beach:
            tourist_destinations.extend(db.session.query(ModelTouristDestination). \
                                        filter(ModelTouristDestination.is_beach == True).all()[:3])
        if maxi == volcano:
            tourist_destinations.extend(db.session.query(ModelTouristDestination). \
                                        filter(ModelTouristDestination.is_volcano == True).all()[:3])
        if maxi == forest:
            tourist_destinations.extend(db.session.query(ModelTouristDestination). \
                                        filter(ModelTouristDestination.is_forest == True).all()[:3])
        if maxi == mountain:
            tourist_destinations.extend(db.session.query(ModelTouristDestination). \
                                        filter(ModelTouristDestination.is_mountain == True).all()[:3])
        return tourist_destinations
    else:
        today = date.today()
        season = await get_tourist_destinations_of_season(today.month)

        return season
