import os
from datetime import datetime, timedelta

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext


# se cargan las variables de entorno, donde se encuentra la clave secreta.
load_dotenv(".env")

secret_key = os.environ["SECRET_KEY"]

algorithm = "HS256"

# se establecen los patrones de Seguridad a utilizar
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = secret_key


def create_access_token(data):
    """
    Funcion para crear tokens de acceso para acceder a los endpoint
    que requieran de acceso por parte del usuario
    :param: data: datos que se codificaran en el tocken a crear
    :return token generado con los datos, llave secreta y algoritmos seleccionados
    """
    to_encode = data.copy()
    access_token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return access_token


def get_password_hash(password):
    """
    Funcion para hashear el contenido de una contraseña y regresa el resultado
    :param password: contraseñá en texto plano
    :return codigo hash de la contraseña
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Funcion para verificar si una contraseña conincide con el hash almacenado.
    param: plain_password: contraseña en tento plano
    param: hashed_password: valor hash de la contraseña registrada
    return: verdadero si coninciden, falso en otro caso
    """
    return pwd_context.verify(plain_password, hashed_password)


def encode_token(user_id):
    """
    Funcion para codificar un nuevo token con una fecha de expiración, justo al id
    del usuario al que se le asigna el token.
    : param: user_id: identificador del usuario del token
    : return: un nuevo token
    """
    payload = {
        'exp': datetime.utcnow() + timedelta(days=365, minutes=0),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        secret,
        algorithm='HS256'
    )


def decode_token(token):
    """
    Funcion para decodificar el contenido de un token
    :param token: token utilizado por un usuario
    :return identificador del usuario que usa el token
    :raise: 401: el token ya expiro
    :raise 401: el token es invalido
    """
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Signature has expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


def auth_wrapper(auth: HTTPAuthorizationCredentials = Security(security)):
    """
    Funcion utilizada para verificar la autorización de las credenciales usadas para acceder a un endpoint
    de la API, verifica que el token sea valido, en caso contrario retorna un error HTTP 401.
    auth: credenciales utilizadas para acceder a un endpoint
    """
    return decode_token(auth.credentials)


def decode_access_token(data):
    """
    Funcion
    """
    token_data = jwt.decode(data, secret_key, algorithms=algorithm)
    return token_data
