

from src.authentication import get_password_hash
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from fastapi import status

from src.models import User as ModelUser
from src.schema import User as SchemaUser

user = APIRouter()


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

    if(user.password):
        #hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        db_user.password = user.password  # hashed_password
    if(user.email):
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
