from fastapi import APIRouter, HTTPException
from fastapi import status
from fastapi_sqlalchemy import db

from src.authentication import verify_password, encode_token, get_password_hash
from src.models import User as ModelUser
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
    db_user = db.session.query(ModelUser).filter(
        ModelUser.email == email).one()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


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


@user.get("/users/{user_id}", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def get_user(user_id: int):
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


@user.post("/update-user/{user_id}", response_model=SchemaUser, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: SchemaUser):
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


@user.delete("/delete-user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int):
    db_user = select_user(user_id)

    db.session.delete(db_user)
    db.session.commit()
    return True
