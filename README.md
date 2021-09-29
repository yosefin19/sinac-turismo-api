# sinac-turismo-api

**Para instalar las bibliotecas necesarias usar:**

`pip install requirements.txt`

**Para construir la imagen de Docker de la aplicación:**

`docker-compose build`

**Para iniciar con la ejecución de los contenedores:**

`docker-compose up`
**Para la creación de las tablas en la base de datos inicial:**

`docker-compose run app alembic upgrade head`

**Para actualizar los contenidos de la base de datos:**

`docker-compose run app alembic revision --autogenerate -m "New Migration"`

**Iniciar la configuración de alembic (no necesario):**

`alembic init alembic`


