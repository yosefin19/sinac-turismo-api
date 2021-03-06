import os
import secrets
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from fastapi import status, File, UploadFile
from src.authentication import auth_wrapper
from src.models import Gallery as ModelGallery
from src.schema import Gallery as SchemaGallery
from src.repository import reduce_image_size, remove_image

gallery = APIRouter()


async def add_new_image(path, image):
    image_name = image.filename
    image_extension = image_name.split(".")[-1]

    token_name = f'{secrets.token_hex(10)}.{image_extension}'
    generated_name = path + token_name
    file_content = await image.read()

    os.makedirs(os.path.dirname(os.getcwd() + generated_name), exist_ok=True)

    with open(os.getcwd() + generated_name, "wb") as file:
        file.write(file_content)
    await reduce_image_size(generated_name)
    file.close()
    return generated_name


@gallery.get("/gallery", response_model=SchemaGallery, status_code=status.HTTP_200_OK)
def get_gallery(gallery_id=Depends(auth_wrapper)):
    db_gallery = select_gallery(gallery_id)
    return db_gallery


@gallery.post("/add-gallery", response_model=SchemaGallery, status_code=status.HTTP_201_CREATED)
def add_gallery(gallery_schema: SchemaGallery):
    db_gallery = ModelGallery(photos_path='/', profile_id=gallery_schema.profile_id)

    db.session.add(db_gallery)
    db.session.commit()

    return db_gallery


@gallery.post("/add-photo", status_code=status.HTTP_200_OK)
async def add_gallery_photo(photos: List[UploadFile] = File(...), gallery_id=Depends(auth_wrapper)):
    db_gallery = select_gallery(gallery_id)

    PATH = f'/data_repository/profile/gallery/{gallery_id}/'
    if db_gallery.photos_path == "/":
        photos_path = ""
    else:
        photos_path = db_gallery.photos_path

    path = ''
    for photo in photos:
        path = await add_new_image(PATH, photo)
        if photos_path == "":
            photos_path += path
        else:
            photos_path += "," + path

    db_gallery.photos_path = photos_path
    db.session.commit()
    db.session.refresh(db_gallery)
    return photos_path


@gallery.delete("/delete-photo/{name}", status_code=status.HTTP_200_OK)
async def delete_gallery_photo(name: str, gallery_id=Depends(auth_wrapper)):
    PATH = f'/data_repository/profile/gallery/{gallery_id}'
    if os.path.isdir(os.getcwd() + PATH):
        directory_files = os.listdir(os.getcwd() + PATH)
        for file in directory_files:
            if file == name:
                await remove_image(PATH + "/" + file)

    db_gallery = select_gallery(gallery_id)
    photos_path = db_gallery.photos_path.split(',')
    new_photos_path = ""
    for photo in photos_path:
        filename = photo.split('/')[-1]
        if not (filename == name):
            if new_photos_path == "":
                new_photos_path += photo
            else:
                new_photos_path += ',' + photo

    gallery.photos_path = new_photos_path
    db.session.commit()
    db.session.refresh(db_gallery)

    return new_photos_path


def select_gallery(gallery_id: int):
    db_g = db.session.query(ModelGallery).filter(ModelGallery.profile_id == gallery_id).one()
    if not db_g:
        raise HTTPException(status_code=404, detail="Gallery not found")

    return db_g
