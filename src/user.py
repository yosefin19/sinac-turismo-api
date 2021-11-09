from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from fastapi import status

from src.authentication import verify_password, encode_token, get_password_hash, auth_wrapper
from src.models import User as ModelUser
from src.profile import select_profile_by_user_id
from src.reset_password import new_password_generator, send_email
from src.schema import Authentication as SchemaAuthentication
from src.schema import User as SchemaUser

user = APIRouter()


def select_user_by_email(email: str):
    """
    Funcion para buscar usuarios por correo electronico.
    param: email: correo del usuario que se busca
    return: usuario cuyo correo coincida
    raise: error HTTP 400, no se encontro un usuario
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
    param: auth: credenciales con el correo del usuario.
    return: esquema con el perfil del usuario
    raise: Error no se encuentra un usuario
    """
    db_user = select_user_by_email(auth.email)
    if db_user is None:
        return HTTPException(status_code=400, detail="Email not found")
    return select_profile_by_user_id(db_user.id)


@user.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(auth: SchemaAuthentication):
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
    param: auth: credenciales utilizadas para iniciar sesión
    return: esquema con el token y el tipo correspondiente
    raise: error HTTP 400 el correo o contraseña no funcionan
    """
    db_user = select_user_by_email(auth.email)

    if (db_user is None) or (not verify_password(auth.password, db_user.password)):
        return HTTPException(status_code=400, detail="Email or Password not found")
    else:
        access_token = encode_token(db_user.id)
        return {'token': access_token, 'token_type': 'bearer'}


@user.get("/users", status_code=status.HTTP_200_OK)
def get_users():
    db_users = db.session.query(ModelUser).all()
    if not db_users:
        raise HTTPException(status_code=404, detail="Users not found")
    return db_users


@user.get("/user", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def get_user(user_id=Depends(auth_wrapper)):
    user = select_user(user_id)
    return user


def select_user(user_id: int):
    db_user = db.session.query(ModelUser).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user.post("/add-user", response_model=SchemaUser, status_code=status.HTTP_201_CREATED)
def add_user(user: SchemaUser):
    try:
        hashed_password = get_password_hash(user.password)

        db_user = ModelUser(
            email=user.email, password=hashed_password, admin=user.admin)
        db.session.add(db_user)
        db.session.commit()
        return db_user

    except:
        raise HTTPException(status_code=400, detail="User already exists")


@user.post("/update-user", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def update_user(user: SchemaUser, user_id=Depends(auth_wrapper)):
    db_user = select_user(user_id)

    if user.password:
        hashed_password = get_password_hash(user.password)
        db_user.password = hashed_password
    if user.email:
        db_user.email = user.email
    db_user.admin = user.admin

    db.session.commit()
    db.session.refresh(db_user)
    return db_user


@user.delete("/delete-user", status_code=status.HTTP_200_OK)
async def delete_user(user_id=Depends(auth_wrapper)):
    db_user = select_user(user_id)

    db.session.delete(db_user)
    db.session.commit()
    return True
