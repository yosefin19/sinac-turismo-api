import os
import secrets

from PIL import Image
from fastapi import HTTPException

# Extenciones validas para las imagenes disponibles a cargar
EXTENSIONS = ["png", "jpg", "jpeg"]


async def reduce_image_size(image_path):
    """
    Función utilizada para reducir la resolución de las imagenes registradas.
        :param image_path -> Ruta de la imagen.
    """
    image_path = os.getcwd() + image_path
    image = Image.open(image_path)
    image.save(image_path, optimize=True, quality=70)


async def remove_image(path):
    """
    Función utilizada para eliminar las imagenes registradas en el sistema de archivos.
        :param path: Ruta del archivo a eliminar.
        :raise HTTPException: si el archivo no existe.
    """

    path = os.getcwd() + path
    if os.path.exists(path):
        os.remove(path)
    else:
        raise HTTPException(status_code=404, detail="File not found")


def remove_directory(path):
    """
    Función para eliminar directorios del sistema de archivos.
    :param path: Ruta del directoria a eliminar.
    :raise  HTTPException: si el archivo no existe.
    """

    path = os.getcwd() + path
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        raise HTTPException(status_code=404, detail="File not found")


async def add_new_image(path, image):
    """
    Función para agregar una nueva imagen al sistema de archivos.
    :param path: Ruta en la que se guarda la imagen.
    :param image: Datos correspondientes a una imagen.
    :return: Ruta en la que se guarda + nombre generado.
    :raise: HTTPException: si la extención no es valida.
    """

    image_name = image.filename
    image_extension = image_name.split(".")[-1]
    if not (image_extension in EXTENSIONS):
        raise HTTPException(status_code=400, detail="Image extension not found")
    token_name = f'{secrets.token_hex(10)}.{image_extension}'
    generated_name = path + token_name
    file_content = await image.read()

    os.makedirs(os.path.dirname(os.getcwd() + generated_name), exist_ok=True)

    with open(os.getcwd() + generated_name, "wb") as file:
        file.write(file_content)
    await reduce_image_size(generated_name)
    file.close()
    return generated_name


async def add_conservation_area_photo(directory_name, photos, region_photo):
    """
    Función para guardar las fotografías de un área de conservación.
    :param directory_name: Nombre del directorio donde se guardaran los archivos.
    :param photos: Lista de datos correspondientes a una imagen.
    :param region_photo: Datos correspondientes a una imagen.
    :return: photos_path, region_path: Tupla de strings con las rutas de las imagenes y mapa de la región.
    """

    PATH = f'/data_repository/conservation_area/{directory_name}/'
    region_path = await add_new_image(PATH, region_photo)
    photos_path = []
    for photo in photos:
        photos_path.append(await add_new_image(PATH, photo))
    if photos_path:
        photos_path = ",".join(photos_path)
    else:
        photos_path = ''
    return photos_path, region_path


async def update_conservation_area_photo(conservation_area, directory_name, photos, region_photo):
    """
    Función para actualizar las fotografías de un área de conservación.
    :param conservation_area: Objeto con los datos asociados a un área de conservación.
    :param directory_name: Nombre del directorio en el que se almacenan los datos.
    :param photos: Lista de datos correspondientes a una imagen.
    :param region_photo: Datos correspondientes a una imagen.
    :return new_photos_path, region_path: Tupla de strings con los valores actualizados.
    """

    PATH = f'/data_repository/conservation_area/{directory_name}/'

    region_path = conservation_area.region_path
    if (PATH + region_photo.filename) != region_path:
        await remove_image(conservation_area.region_path)
        region_path = await add_new_image(PATH, region_photo)

    photos_path = conservation_area.photos_path.split(',')
    photos_file_name = [x.split('/')[-1] for x in photos_path]
    new_photos_path = list()
    for photo in photos:
        if not (photo.filename in photos_file_name):
            new_photos_path.append(await add_new_image(PATH, photo))
        else:  # es necesario reenviar todas las fotografías nuevamente.
            index = photos_file_name.index(photo.filename)
            new_photos_path.append(photos_path[index])
            photos_file_name.pop(index)

    #  Se eliminan del sistema de archivos las que ya no son necesarias.
    for filename in photos_file_name:
        await remove_image(PATH + filename)
    new_photos_path = ','.join(new_photos_path)

    return new_photos_path, region_path


async def delete_conservation_area_photo(conservation_area_id):
    """
    Función utilizada para eliminar el directorio y archivos asociados a un área de conservación.
    :param conservation_area_id: Identificador del área de conservación a eliminar.
    """
    directory_name = f'{conservation_area_id}_dir'
    PATH = f'/data_repository/conservation_area/{directory_name}/'
    directory_files = os.listdir(os.getcwd() + PATH)
    if os.path.isdir(os.getcwd() + PATH):
        directory_files = os.listdir(os.getcwd() + PATH)
        for file in directory_files:
            await remove_image(PATH + file)
        remove_directory(PATH)


async def add_tourist_destination_photo(directory_name, photos):
    """
    Función para registrar las fotografías de un destino turístico
    :param directory_name: Nombre del directorio en el que se almacenaran las fotografías.
    :param photos: Lista de datos correspondientes a una imagen.
    :return photos_path: String separado por coma con las rutas de las fotografías.
    """

    PATH = f'/data_repository/tourist_destination/{directory_name}/'
    photos_path = []
    for photo in photos:
        photos_path.append(await add_new_image(PATH, photo))
    if photos_path:
        photos_path = ",".join(photos_path)
    else:
        photos_path = ''
    return photos_path


async def update_tourist_destination_photo(photos_path, directory_name, photos):
    """
    Función para actualizar las fotografías de un destino turístico del sistema de archivos.
    :param photos_path: Ruta de los archivos previamente agregados.
    :param directory_name: Directorio en el cual se almacenan los archivos en el sistema de archivos.
    :param photos: Lista de datos correspondientes a una imagen.
    :return new_photos_path: String separado con comas, con las rutas actualizadas.
    """

    PATH = f'/data_repository/tourist_destination/{directory_name}/'
    photos_path_split = photos_path.split(',')
    photos_file_name = [path.split('/')[-1] for path in photos_path_split]
    new_photos_path = list()
    for photo in photos:
        if not (photo.filename in photos_file_name):
            new_photos_path.append(await add_new_image(PATH, photo))
        else:  # es necesario reenviar todas las fotos nuevamente.
            index = photos_file_name.index(photo.filename)
            new_photos_path.append(photos_file_name[index])
            photos_file_name.pop(index)

    # Se eliminan las que ya no son necesarias del sistema de archivos.
    for filename in photos_file_name:
        await remove_image(PATH + filename)

    new_photos_path = ','.join(new_photos_path)
    return new_photos_path


async def delete_tourist_destination_photo(tourist_destination_id):
    """
    Función para eliminar el directorio de un destino turístico del sistema de archivos.
    :param tourist_destination_id: identificador del destino turístico
    """

    directory_name = f'{tourist_destination_id}_dir'
    PATH = f'/data_repository/tourist_destination/{directory_name}/'
    if os.path.isdir(os.getcwd() + PATH):
        directory_files = os.listdir(os.getcwd() + PATH)
        for file in directory_files:
            await remove_image(PATH + file)
        remove_directory(PATH)


async def add_review_photo(directory_name, photo):
    """
    Función para registrar las fotografías de una opinión para un destino turístico
    :param directory_name: Nombre del directorio en el que se almacenará las fotografía.
    :param photo: Datos correspondientes a una imagen.
    :return photos_path: Rutas de las fotografía.
    """

    PATH = f'/data_repository/tourist_destination_review/{directory_name}/'
    photo_path = await add_new_image(PATH, photo)
    return photo_path


async def update_review_photo(photo_path, directory_name, photo):
    """
    Función para actualizar las fotografías de una opinión de un destino turístico del sistema de archivos.
    :param photo_path: Ruta del archivo previamente agregado.
    :param directory_name: Directorio en el cual se almacenan los archivos en el sistema de archivos.
    :param photo: Datos correspondientes a una imagen.
    :return new_photos_path: String con las ruta actualizada.
    """

    PATH = f'/data_repository/tourist_destination_review/{directory_name}/'
    photo_file_name = photo_path.split('/')[-1]

    if not (photo.filename in photo_file_name):
        new_path = await add_new_image(PATH, photo)
    else:
        await remove_image(PATH + photo_file_name)
        new_path = await add_new_image(PATH, photo)

    return new_path


async def delete_review_photo(tourist_destination_id, user_id):
    """
    Función para eliminar el directorio de un destino turístico del sistema de archivos.
    :param tourist_destination_id: identificador del destino turístico
    :param user_id: identificador del usuario
    """

    directory_name = f'{tourist_destination_id}-{user_id}_dir'
    PATH = f'/data_repository/tourist_destination_review/{directory_name}/'
    if os.path.isdir(os.getcwd() + PATH):
        directory_files = os.listdir(os.getcwd() + PATH)
        for file in directory_files:
            await remove_image(PATH + file)
        remove_directory(PATH)
