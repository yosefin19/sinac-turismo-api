from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from fastapi import status
from src.authentication import auth_wrapper

from src.models import User as ModelUser
from src.schema import User as SchemaUser

user = APIRouter()

@user.get("/users", status_code=status.HTTP_200_OK)
def get_users():
    db_users = db.session.query(ModelUser).all()
    if not db_users:
        raise HTTPException(status_code=404, detail="Users not found")
    return db_users


@user.get("/user",response_model=SchemaUser, status_code=status.HTTP_200_OK)
def get_user(user_id = Depends(auth_wrapper)):
    user = select_user(user_id)
    return user


def select_user(user_id: int):
    db_user = db.session.query(ModelUser).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user.post("/add-user", response_model=SchemaUser, status_code=status.HTTP_201_CREATED)
def add_user(user: SchemaUser):
    #hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = ModelUser(email=user.email, password=user.password, admin=user.admin)
    db.session.add(db_user)
    db.session.commit()
    return db_user


@user.post("/update-user}",response_model=SchemaUser, status_code=status.HTTP_200_OK)
def update_user( user: SchemaUser, user_id = Depends(auth_wrapper) ):

    db_user = select_user(user_id)

    if(user.password):
        #hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        db_user.password = user.password# hashed_password
    if(user.email ):
        db_user.email = user.email
    db_user.admin = user.admin

    db.session.commit()
    db.session.refresh(db_user)
    return db_user


@user.delete("/delete-user", status_code=status.HTTP_200_OK)
async def delete_user(user_id = Depends(auth_wrapper)):
    db_user = select_user(user_id)

    db.session.delete(db_user)
    db.session.commit()
    return True 



