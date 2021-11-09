import random
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv

"""
Largo de las contraseñas que se generan
"""
PASSWORD_LEN = 12

"""
Caracteres que corresponden al alfabeto utilizado para la creación
de la contraseña aleatoria.
"""
DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

LOW_CASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                       'u', 'v', 'w', 'x', 'y', 'z']

UP_CASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q', 'R', 'S', 'T',
                      'U', 'V', 'W', 'X', 'Y', 'Z']

ALPHABET = DIGITS + UP_CASE_CHARACTERS + LOW_CASE_CHARACTERS


def new_password_generator():
    """
    Función para generar una string aleatoria con el Alfabeto establecido, selecciona
    los caracteres necesarios y agrega hasta completar con el largo establecido.
    :return string aleatorio
    """
    # Caracteres necesarios en la contraseña
    random_digit = random.choice(DIGITS)
    random_up_letter = random.choice(UP_CASE_CHARACTERS)
    random_low_letter = random.choice(LOW_CASE_CHARACTERS)
    generate_password = f"{random_digit}{random_up_letter}{random_low_letter}"
    password_list = list()
    for x in range(PASSWORD_LEN):
        # se selecciona un caracter del alfabeto
        generate_password = generate_password + random.choice(ALPHABET)
        password_list = list(generate_password)
        # se mezcla el contenido generado
        random.shuffle(password_list)
    new_password = ''.join(password_list)
    return new_password


"""
Variables de entorno para el envío de correo electronico
"""
load_dotenv('.env')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')


async def send_email(recipient: str, body: dict):
    conf = ConnectionConfig(
        MAIL_USERNAME=Envs.MAIL_USERNAME,
        MAIL_PASSWORD=Envs.MAIL_PASSWORD,
        MAIL_FROM=Envs.MAIL_FROM,
        MAIL_PORT=Envs.MAIL_PORT,
        MAIL_SERVER=Envs.MAIL_SERVER,
        MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True,
        TEMPLATE_FOLDER='./assets/email'
    )
    message = MessageSchema(
        subject="Nueva contraseña - SINAC turismo",
        recipients=[recipient],
        template_body=body,
        subtype="html"
    )

    fast_mail = FastMail(conf)
    await fast_mail.send_message(message, template_name='reset_password.html')
    return {"status_code": "200", "message": "Email has been sent"}
