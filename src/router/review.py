from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from fastapi import File, UploadFile, status, Depends

from src.models import Review as ModelReview
from src.schema import Review as SchemaReview

from src.authentication import auth_wrapper

review_router = APIRouter()


def formatDate(date):
    month = ["ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]

    return date.strftime("%d de " + month[date.month - 1] + ". %Y")


def select_review(review_id: int):
    """
    Función para buscar la información de una opinión de un usuario sobre un destino.
    :param review_id: Identificador de la relación.
    :return db_favorites_area_id: Información de la opinión.
    """
    db_review = db.session.query(ModelReview).get(review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_review.date = formatDate(db_review.date)
    return db_review


@review_router.get('/tourist-destination/{tourist_destination_id}/reviews', response_model=SchemaReview, status_code=status.HTTP_200_OK)
def get_user_review(tourist_destination_id: int):  # user_id=Depends(auth_wrapper)
    """
    Función para buscar la opinión de un usuario en un destino.
    :user_id: Identificador del usuario.
    :param tourist_destination_id: Identificador del destino.
    :return review: Opinión del destino.
    """
    user_id = 1

    for review in db.session.query(ModelReview).filter(ModelReview.user_id == user_id).all():
        if (review.tourist_destination_id == tourist_destination_id):
            return review

    raise HTTPException(status_code=404, detail="Item not found")


@review_router.get('/tourist-destination/{tourist_destination_id}/review')
def get_reviews(tourist_destination_id: int):
    """
    Función para buscar las opiniones de un destino.
    :param tourist_destination_id: Identificador del destino.
    :return reviews: Lista de opiniones del destino.
    """
    # average = 0
    reviews = db.session.query(ModelReview).filter(
        ModelReview.tourist_destination_id == tourist_destination_id).order_by(ModelReview.date.desc()).all()

    for review in reviews:
        review.date = formatDate(review.date)
    # average /= reviews.len()

    return reviews


@review_router.post('/tourist-destination/{tourist_destination_id}/review', response_model=SchemaReview, status_code=status.HTTP_201_CREATED)
def add_review(tourist_destination_id: int, review: SchemaReview):
    # def add_review(tourist_destination_id: int, review: SchemaReview, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para agregar información de una nueva opinión.
    :param tourist_destination_id: Identificador del destino turístico.
    :param review: DTO con los datos a almacenar.
    :param user_id: Identificador del usuario.
    :return: DAO de un destino turístico con los datos actualizados.
    """

    user_id = 1

    # Photos

    db_review = ModelReview(title=review.title,
                            text=review.text,
                            date=datetime.now(),  # .strftime("%Y-%m-%dT%H:%M:00Z"),
                            calification=review.calification,
                            image_path=review.image_path,
                            user_id=user_id,
                            tourist_destination_id=tourist_destination_id)

    print(db_review.date)
    db.session.add(db_review)
    db.session.commit()
    db_review.date = datetime.now()
    return db_review


@review_router.post('/tourist-destination/{tourist_destination_id}/review-image')
async def add_review_image(tourist_destination_id: int, image: UploadFile = File(...)):
    # def add_review(tourist_destination_id: int, review: SchemaReview, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para agregar una imagen a una nueva opinión.
    :param tourist_destination_id: Identificador del destino turístico.
    :param image: Datos correspondientes a una imagen.
    :param user_id: Identificador del usuario.
    :return: Path de la imagen almacenada.
    """

    new_directory_name = f'{tourist_destination_id}-{user_id}_dir'
    photo_path = await repository.add_review_photo(new_directory_name, image)
    return photo_path


@review_router.patch("/tourist-destination/{tourist_destination_id}/review/{review_id}",
                     response_model=SchemaReview, status_code=status.HTTP_200_OK)
def update_review(review_id: int, review: SchemaReview):
    """
    Ruta para actualizar los datos de una opinión.
    :param review_id: identificador de la opinión.
    :param review: DTO con los nuevos datos.
    :return db_review: DAO con los datos actualizados.
    """
    db_review = select_review(review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = review.dict(exclude_unset=True)

    # update photos

    for key, value in update_data.items():
        setattr(db_review, key, value)

    db.session.add(db_review)
    db.session.commit()
    db.session.refresh(db_review)
    return db_review


@review_router.delete('/tourist-destination/{tourist_destination_id}/review/{review_id}', status_code=status.HTTP_200_OK)
def delete_review(review_id: int, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para eliminar un destino favorita.
    :param user_id: Identificador del usuario.
    :return boolean: Verdadero si fue correctamente eliminado.
    """
    db_review = select_review(review_id)
    if(db_review.user_id != user_id):
        return False

    # Photos

    db.session.delete(db_review)
    db.session.commit()
    return True
