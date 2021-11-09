from typing import List

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from fastapi import File, UploadFile, status, Depends

from src.models import TouristDestination as ModelTouristDestination
from src.schema import TouristDestination as SchemaTouristDestination

from src.models import FavoriteDestination as ModelFavoriteDestination
from src.schema import FavoriteDestination as SchemaFavoriteDestination
from src.models import VisitedDestination as ModelVisitedDestination
from src.schema import VisitedDestination as SchemaVisitedDestination

from src import repository

from src.authentication import auth_wrapper

tourist_destination_router = APIRouter()


def select_tourist_destination(tourist_destination_id: int):
    """
    Función para buscar un destino turístico en la base de datos mediante un identificador.
    :param tourist_destination_id: identificador de un área de conservación.
    :return db_tourist_destination: DAO de un área de conservación.
    :raise: HTTPException: no se encontro el identificador.
    """
    db_tourist_destination = db.session.query(
        ModelTouristDestination).get(tourist_destination_id)
    if db_tourist_destination is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_tourist_destination


@tourist_destination_router.post("/tourist-destination", response_model=SchemaTouristDestination,
                                 status_code=status.HTTP_201_CREATED)
def add_tourist_destination(tourist_destination: SchemaTouristDestination):
    """
    Ruta utilizada para agregar información de un nuevo destino turístico.
    :param tourist_destination: DTO con los datos a almacenar.
    :return db_tourist_destination: DAO de un destino turístico con los datos.
    """
    db_tourist_destination = ModelTouristDestination(name=tourist_destination.name,
                                                     description=tourist_destination.description,
                                                     schedule=tourist_destination.schedule,
                                                     fare=tourist_destination.fare,
                                                     contact=tourist_destination.contact,
                                                     recommendation=tourist_destination.recommendation,
                                                     difficulty=tourist_destination.difficulty,
                                                     latitude=tourist_destination.latitude,
                                                     longitude=tourist_destination.longitude,
                                                     hikes=tourist_destination.hikes,
                                                     photos_path=tourist_destination.photos_path,
                                                     is_beach=tourist_destination.is_beach,
                                                     is_forest=tourist_destination.is_forest,
                                                     is_volcano=tourist_destination.is_volcano,
                                                     is_mountain=tourist_destination.is_mountain,
                                                     start_season=tourist_destination.start_season,
                                                     end_season=tourist_destination.end_season,
                                                     conservation_area_id=tourist_destination.conservation_area_id)
    db.session.add(db_tourist_destination)
    db.session.commit()
    return db_tourist_destination


@tourist_destination_router.post("/tourist-destination/{tourist_destination_id}/photos",
                                 response_model=SchemaTouristDestination, status_code=status.HTTP_201_CREATED)
async def add_tourist_destination_photos(tourist_destination_id: int, photos: List[UploadFile] = File(...)):
    """
    Ruta para agregar fotografías a un destino turístico.
    :param tourist_destination_id: identificador de un destino turístico.
    :param photos: Lista de datos correspondientes a una imagen.
    :return db_tourist_destination: DAO con los datos actualizados de las rutas de almacenamiento de las imagenes.
    """
    db_tourist_destination = select_tourist_destination(tourist_destination_id)

    new_directory_name = f'{db_tourist_destination.id}_dir'
    photos_path = await repository.add_tourist_destination_photo(new_directory_name, photos)

    db_tourist_destination.photos_path = photos_path
    db.session.commit()
    db.session.refresh(db_tourist_destination)
    return db_tourist_destination


@tourist_destination_router.get("/tourist-destination", status_code=status.HTTP_200_OK)
def get_tourist_destination():
    """
    Ruta para obtener todos los destinos turisticos
    :return tourist_destination: lista con DAO de todos los destinos registrados.
    """
    tourist_destination = db.session.query(ModelTouristDestination).all()
    return tourist_destination


@tourist_destination_router.get("/tourist-destination/{tourist_destination_id}",
                                response_model=SchemaTouristDestination, status_code=status.HTTP_200_OK)
def get_tourist_destination(tourist_destination_id: int):
    """
    Ruta para obtener un destino turístico mediante identificador.
    :param tourist_destination_id: identificador de un destino turístico.
    :return tourist_destination: DAO del destino turístico registrado.
    """
    tourist_destination = select_tourist_destination(tourist_destination_id)
    return tourist_destination


# conservation-area/{conservation_area_id}
@tourist_destination_router.post("/tourist-destination/update/{tourist_destination_id}",
                                 response_model=SchemaTouristDestination, status_code=status.HTTP_200_OK)
def update_tourist_destination(tourist_destination_id: int, tourist_destination: SchemaTouristDestination):
    """
    Ruta para actualizar los datos de un destino turístico.
    :param tourist_destination_id: identificador del destino turístico.
    :param tourist_destination: DTO con los nuevos datos.
    :return db_tourist_destination: DAO con los datos actualizados.
    """
    db_tourist_destination = select_tourist_destination(tourist_destination_id)

    db_tourist_destination.name = tourist_destination.name
    db_tourist_destination.description = tourist_destination.description
    db_tourist_destination.schedule = tourist_destination.schedule
    db_tourist_destination.fare = tourist_destination.fare
    db_tourist_destination.contact = tourist_destination.contact
    db_tourist_destination.recommendation = tourist_destination.recommendation
    db_tourist_destination.difficulty = tourist_destination.difficulty
    db_tourist_destination.latitude = tourist_destination.latitude
    db_tourist_destination.latitude = tourist_destination.longitude
    db_tourist_destination.hikes = tourist_destination.hikes
    db_tourist_destination.photos_path = tourist_destination.photos_path
    db_tourist_destination.is_beach = tourist_destination.is_beach
    db_tourist_destination.is_forest = tourist_destination.is_forest
    db_tourist_destination.is_volcano = tourist_destination.is_volcano
    db_tourist_destination.is_mountain = tourist_destination.is_mountain
    db_tourist_destination.start_season = tourist_destination.start_season
    db_tourist_destination.end_season = tourist_destination.end_season

    db.session.commit()
    db.session.refresh(db_tourist_destination)
    return db_tourist_destination


@tourist_destination_router.post("/tourist-destination/update/{tourist_destination_id}/photos",
                                 response_model=SchemaTouristDestination, status_code=status.HTTP_200_OK)
async def update_tourist_destination_photos(tourist_destination_id: int, photos: List[UploadFile] = File(...)):
    """
    Ruta para actualizar las fotografías asociadas a un destino turístico.
    :param tourist_destination_id: identificador del destino turístico.
    :param photos: Lista de datos de imagenes a registrar.
    :return db_tourist_destination: DAO con las rutas de las fotografías actualizadas.
    """
    db_tourist_destination = select_tourist_destination(tourist_destination_id)

    directory_name = f'{db_tourist_destination.id}_dir'
    photos_path = await repository.update_tourist_destination_photo(db_tourist_destination.photos_path,
                                                                    directory_name, photos)

    db_tourist_destination.photos_path = photos_path
    db.session.commit()
    db.session.refresh(db_tourist_destination)
    return db_tourist_destination


@tourist_destination_router.delete("/tourist-destination/{tourist_destination_id}",
                                   status_code=status.HTTP_200_OK)
async def delete_tourist_destination(tourist_destination_id: int):
    """
    Ruta utilizada para eliminar todos los datos asociados a un destino turístico.
    :param tourist_destination_id: identificador del destino turístico a eliminar.
    :return boolean: Verdadedo si se completa correctamente.
    """
    db_tourist_destination = select_tourist_destination(tourist_destination_id)

    await repository.delete_tourist_destination_photo(db_tourist_destination.id)

    db.session.delete(db_tourist_destination)
    db.session.commit()
    return True


def select_favorite_destination(favorite_destination_id: int):
    """
    Función para buscar la información de un destino marcado como favorito para un usuario.
    :param favorite_destination_id: Identificador de la relación.
    :return db_favorite_destination: Información del destino marcada como favorito.
    """
    db_favorite_destination = db.session.query(
        ModelFavoriteDestination).get(favorite_destination_id)
    if db_favorite_destination is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_favorite_destination


@tourist_destination_router.get('/tourist-destination/all/favorite')
def get_favorite_destinations(user_id=Depends(auth_wrapper)):
    """
    Función para buscar los destinos favoritos de un usuario.
    :param user_id: Identificador del usuario.
    :return tourist_destinations: Lista de destinos favoritos.
    """
    favorite_destinations = []
    for favorite_destination in db.session.query(ModelFavoriteDestination).filter(ModelFavoriteDestination.user_id == user_id).all():
        favorite_destinations.append(favorite_destination)

    def getIds(item):
        return [item.tourist_destination_id, item.id]
    favorite_destinations_id = list(map(getIds, favorite_destinations))

    tourist_destinations = []
    for tourist_destination in db.session.query(ModelTouristDestination).all():
        for i in range(len(favorite_destinations_id)):
            if tourist_destination.id == favorite_destinations_id[i][0]:
                tourist_destination.favorite_id = favorite_destinations_id[i][1]
                tourist_destinations.append(tourist_destination)
                break
    return tourist_destinations


@tourist_destination_router.get('/tourist-destination/{tourist_destination_id}/favorite')
def get_favorite_destination_id(tourist_destination_id: int, user_id=Depends(auth_wrapper)):
    """
    Función para identificar si un destino está marcado como favorito.
    :param tourist_destination_id: Identificador del destino turístico.
    :param user_id: Identificador del usuario.
    :return El identificador de la relación o cero.
    """
    for favorite_destination in db.session.query(ModelFavoriteDestination).filter(ModelFavoriteDestination.user_id == user_id).all():
        if (favorite_destination.tourist_destination_id == tourist_destination_id):
            return favorite_destination.id

    return 0


@tourist_destination_router.post('/tourist-destination/{tourist_destination_id}/favorite', response_model=SchemaFavoriteDestination, status_code=status.HTTP_201_CREATED)
def add_favorite_destination(tourist_destination_id: int, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para agregar información de un nuevo destino favorito.
    :param tourist_destination_id: Identificador del destino turístico.
    :param user_id: Identificador del usuario.
    :return: DAO de un destino turístico con los datos actualizados.
    """
    db_favorite_destination = ModelFavoriteDestination(user_id=user_id,
                                                       tourist_destination_id=tourist_destination_id)

    db.session.add(db_favorite_destination)
    db.session.commit()
    return db_favorite_destination


@tourist_destination_router.delete('/tourist-destination/all/favorite/{favorite_destination_id}', status_code=status.HTTP_200_OK)
def delete_favorite_destination(favorite_destination_id: int, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para eliminar un destino favorita.
    :param user_id: Identificador del usuario.
    :return boolean: Verdadero si fue correctamente eliminado.
    """
    db_favorite_destination = select_favorite_destination(
        favorite_destination_id)
    if(db_favorite_destination.user_id != user_id):
        return False

    db.session.delete(db_favorite_destination)
    db.session.commit()
    return True


def select_visited_destination(visited_destination_id: int):
    """
    Función para buscar la información de un destino marcado como visitado para un usuario.
    :param visited_destination_id: Identificador de la relación.
    :return db_visited_destination: Información del destino marcada como visitado.
    """
    db_visited_destination = db.session.query(
        ModelVisitedDestination).get(visited_destination_id)
    if db_visited_destination is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_visited_destination


@tourist_destination_router.get('/tourist-destination/all/visited')
def get_visited_destinations(user_id=Depends(auth_wrapper)):
    """
    Función para buscar los destinos visitados por un usuario.
    :param user_id: Identificador del usuario.
    :return tourist_destinations: Lista de destinos visitados.
    """
    visited_destinations = []
    for visited_destination in db.session.query(ModelVisitedDestination).filter(ModelVisitedDestination.user_id == user_id).all():
        visited_destinations.append(visited_destination)

    def getIds(item):
        return [item.tourist_destination_id, item.id]
    visited_destinations_id = list(map(getIds, visited_destinations))

    tourist_destinations = []
    for tourist_destination in db.session.query(ModelTouristDestination).all():
        for i in range(len(visited_destinations_id)):
            if tourist_destination.id == visited_destinations_id[i][0]:
                tourist_destination.visited_id = visited_destinations_id[i][1]
                tourist_destinations.append(tourist_destination)
                break
    return tourist_destinations


@tourist_destination_router.get('/tourist-destination/{tourist_destination_id}/visited')
def get_visited_destination_id(tourist_destination_id: int, user_id=Depends(auth_wrapper)):
    """
    Función para identificar si un destino está marcado como visitado.
    :param tourist_destination_id: Identificador del destino turístico.
    :param user_id: Identificador del usuario.
    :return El identificador de la relación o cero.
    """
    for favorite_destination in db.session.query(ModelVisitedDestination).filter(ModelVisitedDestination.user_id == user_id).all():
        if (favorite_destination.tourist_destination_id == tourist_destination_id):
            return favorite_destination.id

    return 0


@tourist_destination_router.post('/tourist-destination/{tourist_destination_id}/visited', response_model=SchemaVisitedDestination, status_code=status.HTTP_201_CREATED)
def add_visited_destination(tourist_destination_id: int, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para agregar información de un nuevo destino favorito.
    :param tourist_destination_id: Identificador del destino turístico.
    :param user_id: Identificador del usuario.
    :return: DAO de un destino turístico con los datos actualizados.
    """
    db_visited_destination = ModelVisitedDestination(user_id=user_id,
                                                     tourist_destination_id=tourist_destination_id)

    db.session.add(db_visited_destination)
    db.session.commit()
    return db_visited_destination


@tourist_destination_router.delete('/tourist-destination/all/visited/{visited_destination_id}', status_code=status.HTTP_200_OK)
def delete_visited_destination(visited_destination_id: int, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para eliminar un destino favorita.
    :param user_id: Identificador del usuario.
    :return boolean: Verdadero si fue correctamente eliminado.
    """
    db_visited_destination = select_visited_destination(
        visited_destination_id)
    if(db_visited_destination.user_id != user_id):
        return False

    db.session.delete(db_visited_destination)
    db.session.commit()
    return True

@tourist_destination_router.get("/tourist-destination/conservation-area/{conservation_area_id}")
def get_tourist_destination_by_conservation_area_id(conservation_area_id: int):
    """
    Ruta que resuelve todos los destinos turísticos que pertenecen a
    una misma área de conservación.
    param: conservation_area_id: identificador del área de conservación a obtener los destinos.
    return: arreglo con los destinos asociados al área.
    """
    tourist_destinations = db.session.query(ModelTouristDestination).\
        filter(ModelTouristDestination.conservation_area_id == conservation_area_id).all()
    return tourist_destinations


@tourist_destination_router.get("/tourist-destination/season/{current_month}")
async def get_tourist_destinations_of_season(current_month: int):
    """
    Ruta utilizada para obtener los destinos que se encuentren en temporada en un
    mes en especifico del año, los destinos tienen un mes de inicio y finalización
    de temporada, por lo que se valida si inicia y finaliza un mismo año o no.
    param: current_month: número del mes actual del año
    return: arreglo con los destinos que se encuentren en temporada
    raise: error HTTP 400 si el número de mes actual es mayor a 12.
    """
    if current_month > 12:
        raise HTTPException(status_code=400, detail="Bad Request, month < 12")
    tourist_destinations = db.session.query(ModelTouristDestination).all()
    response = []
    for destination in tourist_destinations:
        init_month = destination.start_season
        final_month = destination.end_season
        if init_month == current_month or final_month == current_month:
            response.append(destination)
        elif init_month < current_month < final_month:
            response.append(destination)
        elif final_month < init_month and not(final_month < current_month < init_month):
            response.append(destination)
    return response


@tourist_destination_router.get("/tourist-destination/conservation-area/{conservation_area_id}")
def get_tourist_destination_by_conservation_area_id(conservation_area_id: int):
    """
    Ruta que resuelve todos los destinos turísticos que pertenecen a
    una misma área de conservación.
    param: conservation_area_id: identificador del área de conservación a obtener los destinos.
    return: arreglo con los destinos asociados al área.
    """
    tourist_destinations = db.session.query(ModelTouristDestination).\
        filter(ModelTouristDestination.conservation_area_id == conservation_area_id).all()
    return tourist_destinations


@tourist_destination_router.get("/tourist-destination/season/{current_month}")
async def get_tourist_destinations_of_season(current_month: int):
    """
    Ruta utilizada para obtener los destinos que se encuentren en temporada en un
    mes en especifico del año, los destinos tienen un mes de inicio y finalización
    de temporada, por lo que se valida si inicia y finaliza un mismo año o no.
    param: current_month: número del mes actual del año
    return: arreglo con los destinos que se encuentren en temporada
    raise: error HTTP 400 si el número de mes actual es mayor a 12.
    """
    if current_month > 12:
        raise HTTPException(status_code=400, detail="Bad Request, month < 12")
    tourist_destinations = db.session.query(ModelTouristDestination).all()
    response = []
    for destination in tourist_destinations:
        init_month = destination.start_season
        final_month = destination.end_season
        if init_month == current_month or final_month == current_month:
            response.append(destination)
        elif init_month < current_month < final_month:
            response.append(destination)
        elif final_month < init_month and not(final_month < current_month < init_month):
            response.append(destination)
    return response

