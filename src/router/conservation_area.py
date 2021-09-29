from typing import List

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from fastapi import File, UploadFile, status

from src.models import ConservationArea as ModelConservationArea
from src.schema import ConservationArea as SchemaConservationArea
from src import repository

conservation_area_router = APIRouter()


def select_conservation_area(conservation_area_id: int):
    """
    Función para buscar un área de conservación en la base de datos mediante un identificador.
    :param conservation_area_id: identificador de un área de conservación.
    :return db_conservation_area: DAO de un área de conservación.
    :raise: HTTPException: no se encontro el identificador.
    """
    db_conservation_area = db.session.query(ModelConservationArea).get(conservation_area_id)
    if db_conservation_area is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_conservation_area


@conservation_area_router.post("/add-conservation-area", response_model=SchemaConservationArea,
                               status_code=status.HTTP_201_CREATED)
def add_conservation_area(conservation_area: SchemaConservationArea):
    """
    Ruta utilizada para agregar información de una nueva área de conservación.
    :param conservation_area: DTO de un área de conservación con los datos que se van a registrar.
    :return: DAO de un área de conservación con los datos actualizados.
    """
    db_conservation_area = ModelConservationArea(name=conservation_area.name,
                                                 description=conservation_area.description,
                                                 photos_path=conservation_area.photos_path,
                                                 region_path=conservation_area.region_path)

    db.session.add(db_conservation_area)
    db.session.commit()
    return db_conservation_area


@conservation_area_router.post('/add-conservation-area/{conservation_area_id}/photos',
                               status_code=status.HTTP_201_CREATED)
async def add_conservation_area_photos(conservation_area_id: int,
                                       photos: List[UploadFile] = File(...), region_photo: UploadFile = File(...)):
    """
    Ruta para agregar fotografías de un área de conservación.
    :param conservation_area_id: identificador de un área de conservación.
    :param photos: Lista de datos correspondientes a una imagen.
    :param region_photo: Datos correspondientes a una imagen.
    :return db_conservation_area:  DAO de un área de conservación con los datos actualizados.
    """
    db_conservation_area = select_conservation_area(conservation_area_id)

    new_directory_name = f'{db_conservation_area.id}_dir'
    photos_path, region_path = await repository.add_conservation_area_photo(new_directory_name, photos, region_photo)
    db_conservation_area.photos_path = photos_path
    db_conservation_area.region_path = region_path

    db.session.commit()
    db.session.refresh(db_conservation_area)
    return db_conservation_area


@conservation_area_router.get("/conservation-area", status_code=status.HTTP_200_OK)
def get_conservation_area():
    """
    Ruta para obtener todas las áreas de conservación registradas.
    :return conservation_areas: Lista de DAO de áreas de conservación.
    """
    conservation_areas = db.session.query(ModelConservationArea).all()
    return conservation_areas


@conservation_area_router.get("/conservation-area/{conservation_area_id}", response_model=SchemaConservationArea,
                              status_code=status.HTTP_200_OK)
def get_conservation_area(conservation_area_id: int):
    """
    Ruta para obtener un áreas de conservación en con un ID especifico.
    :param conservation_area_id: identificador del áreas de conservación
    :return:
    """
    conservation_area = db.session.query(ModelConservationArea).get(conservation_area_id)
    if conservation_area is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return conservation_area


@conservation_area_router.post("/update-conservation-area/{conservation_area_id}",
                               response_model=SchemaConservationArea, status_code=status.HTTP_200_OK)
def update_conservation_area(conservation_area_id: int, conservation_area: SchemaConservationArea):
    """
    Ruta para actualizar los datos asociadas a un área de conservación.
    :param conservation_area_id: identificador del área de conservación a actualizar.
    :param conservation_area: DTO con los datos.
    :return db_conservation_area: DAO con los datos actualizados.
    """
    db_conservation_area = select_conservation_area(conservation_area_id)

    db_conservation_area.name = conservation_area.name
    db_conservation_area.description = conservation_area.description
    db_conservation_area.photos_path = conservation_area.photos_path
    db_conservation_area.region_path = conservation_area.region_path

    db.session.commit()
    db.session.refresh(db_conservation_area)
    return db_conservation_area


@conservation_area_router.post("/update-conservation-area/{conservation_area_id}/photos",
                               response_model=SchemaConservationArea, status_code=status.HTTP_200_OK)
async def update_conservation_area_photos(conservation_area_id: int,
                                          photos: List[UploadFile] = File(...), region_photo: UploadFile = File(...)):
    """
    Ruta utilizada para actualizar las fotografías de un área de conservación.
    :param conservation_area_id: identificador del área de conservación a actualizar.
    :param photos: Lista de datos correspondientes a una imagen.
    :param region_photo: Datos correspondientes a una imagen.
    :return db_conservation_area:  DAO de un área de conservación con los datos actualizados.
    """
    db_conservation_area = select_conservation_area(conservation_area_id)

    directory_name = f'{db_conservation_area.id}_dir'
    photos_path, region_path = await repository.update_conservation_area_photo(db_conservation_area,
                                                                               directory_name, photos, region_photo)
    db_conservation_area.photos_path = photos_path
    db_conservation_area.region_path = region_path

    db.session.commit()
    db.session.refresh(db_conservation_area)
    return db_conservation_area


@conservation_area_router.delete("/delete-conservation-area/{conservation_area_id}", status_code=status.HTTP_200_OK)
async def delete_conservation_area(conservation_area_id: int):
    """
    Ruta utilizada para eliminar un área de conservacíon con los datos asociados.
    :param conservation_area_id: identificador del área de conservación.
    :return booolean: Verdadero si fue correctamente eliminado.
    """
    db_conservation_area = select_conservation_area(conservation_area_id)

    await repository.delete_conservation_area_photo(db_conservation_area.id)

    db.session.delete(db_conservation_area)
    db.session.commit()
    return True  # db_conservation_area or HTTPException(status_code=200, detail="ok")

