from src import repository
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

def select_review_by_user(tourist_destination_id: int, user_id: int):
    """
    Función para buscar la información de la opinión de un usuario a partir de su identificador.
    :param tourist_destination_id: Identificador del destino.
    :param user_id: Identificador del usuario.
    :return db_favorites_area_id: Información de la opinión.
    """
    for review in db.session.query(ModelReview).filter(ModelReview.user_id == user_id).all():
        if (review.tourist_destination_id == tourist_destination_id):
            review.date = datetime.now()#formatDate(review.date)
            return review

    raise HTTPException(status_code=404, detail="Item not found")

@review_router.get('/tourist-destination/{tourist_destination_id}/user-review', response_model=SchemaReview, status_code=status.HTTP_200_OK)
def get_user_review(tourist_destination_id: int, user_id=Depends(auth_wrapper)):
    """
    Función para buscar la opinión de un usuario en un destino.
    :param user_id: Identificador del usuario.
    :param tourist_destination_id: Identificador del destino.
    :return review: Opinión del destino.
    """
    review = select_review_by_user(tourist_destination_id, user_id)
    return review


@review_router.get('/tourist-destination/{tourist_destination_id}/reviews')
def get_reviews(tourist_destination_id: int):
    """
    Función para buscar las opiniones de un destino.
    :param tourist_destination_id: Identificador del destino.
    :return reviews: Lista de opiniones del destino.
    """
    reviews = db.session.query(ModelReview).filter(
        ModelReview.tourist_destination_id == tourist_destination_id).order_by(ModelReview.date.desc()).all()

    for review in reviews:
        review.date = formatDate(review.date)

    return reviews


@review_router.post('/tourist-destination/{tourist_destination_id}/user-review', response_model=SchemaReview, status_code=status.HTTP_201_CREATED)
def add_review(tourist_destination_id: int, review: SchemaReview, user_id=Depends(auth_wrapper)):
    """
    Ruta utilizada para agregar información de una nueva opinión.
    :param tourist_destination_id: Identificador del destino turístico.
    :param review: DTO con los datos a almacenar.
    :param user_id: Identificador del usuario.
    :return: DAO de un destino turístico con los datos actualizados.
    """
    db_review = ModelReview(title=review.title,
                            text=review.text,
                            date=datetime.now(),
                            calification=review.calification,
                            image_path=review.image_path,#photos_path,
                            user_id=user_id,
                            tourist_destination_id=tourist_destination_id)

    db.session.add(db_review)
    db.session.commit()
    db_review.date = datetime.now()
    return db_review


@review_router.post('/tourist-destination/{tourist_destination_id}/review-image')
async def add_review_image(tourist_destination_id: int, image: UploadFile = File(...), user_id=Depends(auth_wrapper)):
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


@review_router.patch("/tourist-destination/{tourist_destination_id}/update-review",
                     response_model=SchemaReview, status_code=status.HTTP_200_OK)
def update_review(tourist_destination_id: int, review: SchemaReview, user_id=Depends(auth_wrapper)):
    """
    Ruta para actualizar los datos de una opinión.
    :param review_id: identificador de la opinión.
    :param review: DTO con los nuevos datos.
    :return db_review: DAO con los datos actualizados.
    """
    db_review = select_review_by_user(tourist_destination_id, user_id)

    update_data = review.dict(exclude_unset=True)

    # if usuario
    # update photos

    #for key, value in update_data.items():
    #    setattr(db_review, key, value)

    db_review.title = update_data.get("title")
    db_review.text = update_data.get("text")
    db_review.date = datetime.now()
    db_review.calification = update_data.get("calification")
    db_review.image_path = update_data.get("image_path")

    db.session.add(db_review)
    db.session.commit()
    db.session.refresh(db_review)
    db_review.date = datetime.now()
    return db_review


@review_router.delete('/tourist-destination/{tourist_destination_id}/user-review/{review_id}', status_code=status.HTTP_200_OK)
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
