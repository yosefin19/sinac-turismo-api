import os
import secrets
from typing import List
from PIL import Image
from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from fastapi import status, File, UploadFile
from src.authentication import auth_wrapper
from src.models import Gallery as ModelGallery
from src.schema import Gallery as SchemaGallery

gallery = APIRouter()

# Extenciones validas para las imagenes disponibles a cargar
EXTENSIONS = ["png", "jpg", "jpeg"]


async def reduce_image_size(image_path):

    image_path = os.getcwd() + image_path
    image = Image.open(image_path)
    image.save(image_path, optimize=True, quality=70)

async def remove_image(path):
    path = os.getcwd() + path
    if os.path.exists(path):
        os.remove(path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

def remove_directory(path):

    path = os.getcwd() + path
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

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

@gallery.get("/gallery",response_model=SchemaGallery, status_code=status.HTTP_200_OK)
def get_gallery(gallery_id = Depends(auth_wrapper)):
    gallery = select_gallery(gallery_id)
    return gallery

@gallery.post("/add-gallery", response_model=SchemaGallery, status_code=status.HTTP_201_CREATED)
def add_gallery(gallery: SchemaGallery):

    db_g = ModelGallery(photos_path = '/',  profile_id = gallery.profile_id)

    db.session.add(db_g)
    db.session.commit()
    
    return db_g

@gallery.post("/add-photo}", status_code=status.HTTP_200_OK)
async def add_gallery_photo(photos: List[UploadFile] = File(...), gallery_id = Depends(auth_wrapper) ):

    PATH = f'/data_repository/profile/gallery/{gallery_id}/'
    photos_path = []
    for photo in photos:
        photos_path.append(await add_new_image(PATH, photo))
    if photos_path:
        photos_path = ",".join(photos_path)
    else:
        photos_path = ''

    db_g = select_gallery(gallery_id)
    db_g.photos_path = photos_path
    db.session.commit()
    db.session.refresh(db_g)
    return photos_path

@gallery.delete("/delete-photo", status_code=status.HTTP_200_OK)
async def delete_gallery_photo(name: str, gallery_id = Depends(auth_wrapper)):

    PATH = f'/data_repository/profile/gallery/{gallery_id}'
    if os.path.isdir(os.getcwd() + PATH):
        directory_files = os.listdir(os.getcwd() + PATH)
        for file in directory_files:
            if(file == name):
                await remove_image(PATH + "/" + file)

    gallery = select_gallery(gallery_id)
    print(gallery.photos_path)
    photos_path = gallery.photos_path.split(',')
    print(photos_path)
    new_photos_path = list()
    for photo in photos_path: 
        filename = photo.split('/')[-1]
        print(filename)
        if not(filename==name):
            print('dentro')
            new_photos_path.append(photo)
    return new_photos_path

def select_gallery(gallery_id: int):
    db_g = db.session.query(ModelGallery).get({"profile_id":gallery_id})
    if not db_g:
        raise HTTPException(status_code=404, detail="Gallery not found")

    return db_g
