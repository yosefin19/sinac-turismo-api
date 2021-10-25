"""
======================================================================
Copyright (C) 2021 Brandon Ledezma, Walter Morales, Yosefin Solano
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see https://www.gnu.org/licenses/.

    Instituto Tecnológico de Costa Rica
    Proyecto de Ingeniería de Software - IC-7602

    SINAC Turismo - API
    Disponible en: https://github.com/yosefin19/sinac-turismo-api
========================================================================
"""


import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI


from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware


from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from src.router.tourist_destination import tourist_destination_router
from src.router.conservation_area import conservation_area_router
from src.user import user
from src.profile import profile


sinac_turismo_api = FastAPI()

# Se establece un directorio para la solicitud de archivos
sinac_turismo_api.mount('/data_repository', StaticFiles(directory="data_repository"), name='data_repository')

# Se cargan las variables de entorno del archivo .env
load_dotenv('.env')

# Se establece el enlace a la base de datos
sinac_turismo_api.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
sinac_turismo_api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta predefinida
@sinac_turismo_api.get("/")
async def root():
    return {'message': "SINAC Turismo API"}

# Se incluyen las rutas de las áreas de conservación
sinac_turismo_api.include_router(conservation_area_router)

# Se incluyen las rutas de los destinos turisticos
sinac_turismo_api.include_router(tourist_destination_router)

# Se incluyen las rutas de los usuarios
sinac_turismo_api.include_router(user)

# Se incluyen las rutas de los perfiles
sinac_turismo_api.include_router(profile)


if __name__ == "__main__":
    uvicorn.run(sinac_turismo_api, host="0.0.0.0", port=8000, reload=True)
