from typing import List

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from fastapi import File, UploadFile, status

from src.models import TouristDestination as ModelTouristDestination
from src.models import ConservationArea as ModelConservationArea
from src.schema import TouristDestination as SchemaTouristDestination

from src import repository

tourist_destination_router = APIRouter()


def select_tourist_destination(tourist_destination_id: int):
    """
    Función para buscar un destino turístico en la base de datos mediante un identificador.
    :param tourist_destination_id: identificador de un área de conservación.
    :return db_tourist_destination: DAO de un área de conservación.
    :raise: HTTPException: no se encontro el identificador.
    """
    db_tourist_destination = db.session.query(ModelTouristDestination).get(tourist_destination_id)
    if db_tourist_destination is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_tourist_destination


@tourist_destination_router.post("/add-tourist-destination", response_model=SchemaTouristDestination,
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
                                                     conservation_area_id=tourist_destination.conservation_area_id)
    db.session.add(db_tourist_destination)
    db.session.commit()
    return db_tourist_destination


@tourist_destination_router.post("/add-tourist-destination/{tourist_destination_id}/photos",
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
@tourist_destination_router.post("/update-tourist-destination/{tourist_destination_id}",
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

    db.session.commit()
    db.session.refresh(db_tourist_destination)
    return db_tourist_destination


@tourist_destination_router.post("/update-tourist-destination/{tourist_destination_id}/photos",
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


@tourist_destination_router.delete("/delete-tourist-destination/{tourist_destination_id}",
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
    return True  # db_tourist_destination HTTPException(status_code=200, detail="ok")
