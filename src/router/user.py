from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from fastapi import status

from src.authentication import verify_password, encode_token, get_password_hash, auth_wrapper
from src.models import User as ModelUser
from src.router.profile import select_profile_by_user_id
from src.reset_password import new_password_generator, send_email
from src.schema import Authentication as SchemaAuthentication
from src.schema import User as SchemaUser

user = APIRouter()


def select_user(user_id: int):
    """
    Función para buscar los usuarios mediante el identificador en la base de datos.
    :param user_id: identificador
    :return db_user: información del usuario
    :raise Error 404: el usuario no se encontro
    """
    db_user = db.session.query(ModelUser).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def select_user_by_email(email: str):
    """
    Funcion para buscar usuarios por correo electronico.
    :param email: correo del usuario que se busca
    :return: usuario cuyo correo coincida
    :raise error  404:, no se encontro un usuario
    """
    try:
        db_user = db.session.query(ModelUser).filter(
            ModelUser.email == email).one()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except:
        raise HTTPException(status_code=400, detail="User not found")


@user.post("/find-user", status_code=status.HTTP_200_OK)
def find_profile_by_email(auth: SchemaAuthentication):
    """
    Ruta para obtener el perfil de un usuario, apartir del correo de un usuario.
    :param auth: credenciales con el correo del usuario.
    :return: esquema con el perfil del usuario
    :raise Error 404: Error no se encuentra un usuario
    """
    db_user = select_user_by_email(auth.email)
    if db_user is None:
        return HTTPException(status_code=400, detail="Email not found")
    return select_profile_by_user_id(db_user.id)


@user.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(auth: SchemaAuthentication):
    """
    Funcionalidad para solicitar una nueva contraseña al correo electrónico para los usuarios registrados.
    :param auth: esquema con el correo del usuario al que se desea cambiar la contraseña.
    :return: estado del envío de la nueva contraseña, una expección en caso de no encontrar el correo.
    """
    db_user = select_user_by_email(auth.email)
    if db_user is None:
        return HTTPException(status_code=400, detail="Email not found")
    new_password = new_password_generator()
    hashed_password = get_password_hash(new_password)
    db_user.password = hashed_password
    db.session.commit()
    db.session.refresh(db_user)
    return await send_email(db_user.email, {"password": new_password})


@user.post("/login", status_code=status.HTTP_200_OK)
def login(auth: SchemaAuthentication):
    """
    Función para iniciar sesión y acceder a los endpoint de los usuarios de
    la aplicación movil, se genera un token para que acceda a las funciones correspondientes.
    :param auth: credenciales utilizadas para iniciar sesión
    :return: esquema con el token y el tipo correspondiente
    :raise Error HTTP 400: el correo o contraseña no funcionan
    """
    db_user = select_user_by_email(auth.email)

    if (db_user is None) or (not verify_password(auth.password, db_user.password)):
        return HTTPException(status_code=400, detail="Email or Password not found")
    else:
        access_token = encode_token(db_user.id)
        return {'token': access_token, 'token_type': 'bearer'}


@user.get("/users", status_code=status.HTTP_200_OK)
def get_users(admin_id=Depends(auth_wrapper)):
    """
    Función utilizada para obtener todos los usuarios registrados en la base de datos.
    :param admin_id: identificador del usuario administrador que obtiene los usuarios.
    :return: Una lista con todos los datos de los usuarios registrados.
    :raise Error 401: No tiene permisos.
    """
    db_user = select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    db_users = db.session.query(ModelUser).all()
    if not db_users:
        raise HTTPException(status_code=404, detail="Users not found")
    return db_users


@user.get("/user", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def get_user(user_id=Depends(auth_wrapper)):
    """
    Función para obtener un usuario apartir de las credenciales
    :param user_id: token asociado a un usuario
    :return: datos del usuario del identificador
    """
    db_user = select_user(user_id)
    return db_user


@user.get("/user/{user_id}", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id=Depends(auth_wrapper), admin_id=Depends(auth_wrapper)):
    """
    Función para obtener un usuario apartir de las credenciales
    :param user_id: identificador del usuario
    :param admin_id: token asociado a un usuario administrador
    :return: datos del usuario del identificador
    """
    db_user = select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    db_user = select_user(user_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    db_user = select_user(user_id)
    return db_user


@user.post("/add-user", response_model=SchemaUser, status_code=status.HTTP_201_CREATED)
def add_user(user_schema: SchemaUser):
    """
    Función utilizada para agregar nuevos usuarios a la base de datos desde la aplicación movil.
    :param user_schema: esquema con los datos asociados a un usuario.
    :return: DTO datos del usuario registrados.
    """
    try:
        hashed_password = get_password_hash(user_schema.password)

        db_user = ModelUser(
            email=user_schema.email, password=hashed_password, admin=user_schema.admin)
        db.session.add(db_user)
        db.session.commit()
        return db_user

    except:
        raise HTTPException(status_code=400, detail="User already exists")


def update_user(user_schema: SchemaUser, user_id: int):
    """
    Función para actualizar un usuario de la base de datos.
    :param user_id: identificador del usuario actualizado.
    :param user_schema: DTO con los datos del usuario.
    :return: DAO con los nuevos datos.
    """
    db_user = select_user(user_id)

    if user_schema.password:
        hashed_password = get_password_hash(user_schema.password)
        db_user.password = hashed_password
    if user_schema.email:
        db_user.email = user_schema.email
    db_user.admin = user_schema.admin

    db.session.commit()
    db.session.refresh(db_user)
    return db_user


@user.post("/update-user", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def update_personal_user(user_schema: SchemaUser, user_id=Depends(auth_wrapper)):
    """
    Función utilizada para actualizar un usuario de la base de datos.
    :param user_schema: esquema con los datos asociados a un usuario, los valores nuevos seran actualizados.
    :param user_id: credenciales de un usuario (Token JWT).
    :return: usuario con los datos actualizados.
    """
    return update_user(user_schema, user_id)


@user.post("/update-user/{user_id}", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def update_user_by_id(user_id: int, user_schema: SchemaUser, admin_id=Depends(auth_wrapper)):
    """
    Función utilizada para actualizar un usuario de la base de datos.
    :param user_id: identificador del usuario que va actualizar
    :param user_schema: esquema con los datos asociados a un usuario, los valores nuevos seran actualizados.
    :param admin_id: credenciales de un usuario administrador.
    :return: usuario con los datos actualizados.
    """
    db_user = select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return update_user(user_schema, user_id)


def delete_user(user_id: int):
    db_user = select_user(user_id)

    db.session.delete(db_user)
    db.session.commit()
    return True


@user.delete("/delete-user", status_code=status.HTTP_200_OK)
async def delete_personal_user(user_id=Depends(auth_wrapper)):
    """
    Función utilizada en la aplicación movil, para que un usuario pueda eliminar su usuario.
    :param user_id: credenciales del usuario.
    :return: verdadero en caso de cumplirse.
    """
    return delete_user(user_id)


@user.delete("/delete-user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_by_id(user_id: int, admin_id=Depends(auth_wrapper)):
    """
    Función utilizada en la aplicación movil, para que un usuario pueda eliminar su usuario.
    :param user_id: credenciales del usuario.
    :param admin_id: credenciales de un usuario administrador.
    :return: verdadero en caso de cumplirse.
    """
    db_user = select_user(admin_id)
    if not db_user.admin:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return delete_user(user_id)
