# Proyecto SINAC Turismo: API

La presente página web fue realizada por Brandon Ledezma Fernández, Walter Morales Vásquez y Yosefin Solano Marín con la finalidad de que sea de utilidad para la organización SINAC en Costa Rica, la cual es encargada de la administración de las áreas protegidas e integra las competencias en materia forestal, vida silvestre  y la protección y conservación del uso de cuencas hidrográficas y sistemas hídricos con el fin de dictar políticas, planificar y ejecutar procesos dirigidos a lograr la sostenibilidad en el manejo de los recursos naturales del país.

## Aplicaciones relacionadas
- SINAC Turismo: Móvil (Aplicación móvil para brindar información sobre áreas de conservación y destinos turísticos) 
https://github.com/yosefin19/sinac-turismo-mobile

- SINAC Turismo: Web (Página web para la administración \[visualización, inserción, modificación y eliminación\] de la información)
https://github.com/yosefin19/sinac-turismo-web

- SINAC Turismo: API (API donde se obtiene y registra la información relacionada con las aplicaciones) 
https://github.com/yosefin19/sinac-turismo-api

## Objetivo

Con el desarrollo de esta API se desea poseer un lugar donde obtener y modificar la información que es solicitada por la aplicación móvil de turismo y la página web administrativa. La finalidad de esto concluye en resolver el problema de que los turistas costarricenses o internacionales que visitan la página del SINAC requieren de un fácil acceso a la información de sitios turísticos registrados por dicha organización, asimismo, existe la necesidad de poder mejorar el proceso de compra y reserva para visitar estos lugares. Esta aplicación plantea permitir a los turistas realizar dichas acciones de una forma centralizada y rápida, así como también poder compartir sus experiencias en los destinos registrados con las demás personas.

## Requerimientos generales

### 1 Acceso a información de áreas de conservación
El sistema permitirá a los visitantes poder seleccionar una área de conservación para obtener información sobre la zona, en esta sección el visitante podrá observar un listado de imágenes de la zona, el nombre del área, además el usuario puede marcar esta como favorito y observar la ubicación sobre el mapa del mismo.
### 2 Acceso a información de destinos turísticos
El sistema debe permitir a los visitantes poder seleccionar un destino turístico para obtener información sobre dicho destino, cada uno tendrá nombre, descripción, un listado de fotografías de diferentes puntos del lugar, horario de atención, tarifas de entradas, recomendaciones para la visita, dificultad de la estadía y sus zonas, y ubicación exacta en el mapa.
### 3 Búsqueda y filtrado de destinos
El sistema permitirá a los usuarios realizar la búsqueda de destinos para visitar u obtener información sobre el mismo. Además, debe poseer funcionalidad para filtrar los destinos turísticos según las etiquetas de playa, montaña, bosque y volcán, según lo que el usuario se encuentre buscando.
### 4 Opiniones de usuarios
El sistema permite a los usuarios poder comentar sus opiniones sobre el destino con los demás usuarios, para que estos compartan un comentario, fotografías y su calificación.
### 5 Favoritos
El usuario puede marcar como favorito cualquier área de conservación o destino turístico desde la sección propia de cada uno o desde los lugares donde se encuentren listados en la aplicación.
### 6 Registro y manejo de usuarios
Un usuario puede registrarse en la aplicación y actualizar datos como su correo electrónico, nombre, número de teléfono, foto de perfil y banner. Una vez iniciada la sesión esta se mantiene activa hasta que el usuario decida cerrarla.
### 7 Administración de áreas de conservación
Un usuario administrador puede realizar funciones de creación, lectura, actualización y eliminación de las áreas de conservación en la aplicación. En esta podrá aplicar lo anterior a un listado de imágenes de la zona, el nombre del área y la ubicación sobre el mapa del mismo.
### 8 Administración de destinos turísticos.
Deberá existir un conjunto de opciones para crear, mostrar, modificar y eliminar destinos turísticos para usuarios administradores. Cada destino turístico tendrá nombre, descripción, fotografías, horario, tarifas, recomendaciones, dificultad y ubicación exacta en el mapa.
### 9 Administración de usuarios.
Un administrador es capaz de realizar funciones de creación, lectura, actualización y eliminación de los usuarios en la aplicación. Presenta campos para nombre de usuario, correo electrónico, contraseña y teléfono. La contraseña del usuario deberá encontrarse cifrada.
### 10 Administración de perfiles.
Deberá existir un conjunto de opciones para crear, actualizar, mostrar y eliminar perfiles de usuarios para usuarios administradores. Cada perfil contiene el nombre, correo electrónico, número telefónico y contraseña de un usuario.

## Ejecución de programa

- Es necesario contar con la instalación de python, pip, docker y docker-compose en las últimas versiones.

- Seguidamente es necesario clonar o descargar el contenido del repositorio sinac-turismo-api en donde se vaya a ejecutar.

- Es necesario establecer un ambiente virtual de Python para la ejecución.

- Se deben instalar todas las bibliotecas necesarias de Python con el comando:

```console
pip install -r requirements.txt
```

- Es necesario crear un directorio en el cual se van a guardar los archivos que se ingresen desde los servicios:

```console
mkdir data_repository
```

- La primera ejecución es necesario construir los contenedores, se utiliza el comando:

```console
docker-compose build
```

- Una vez creados los contenedores no es necesario volver a ejecutarlo, únicamente se hace uso del comando:

```console
docker-compose up
```

- Para la primera ejecución es necesario crear los esquemas de la base de datos, haciendo uso de alembic, mediante el comando:

```console
docker-compose run app alembic upgrade head
```

- Para hacer uso nuevas migraciones con los datos nuevos a la base de datos se hace uso de alembic y el comando, es necesario reiniciar los contenedores una vez ejecutado:

```console
docker-compose run app alembic revision --autogenerate -m "New Migration"
docker-compose build
```

## Estado

La aplicación funciona completamente, implementando todas las funcionalidades que fueron solicitadas. Se realizaron las pruebas de funcionalidad correspondientes a cada uno de los componentes.

## Realizado por:

* Brandon Ledezma Fernández
* Walter Morales Vásquez
* Yosefin Solano Marín 
