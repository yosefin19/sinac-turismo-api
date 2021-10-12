from pydantic import BaseModel


"""
Se establecen los objetos de transferencia de datos (DTO), esquemas que son utilizados para
transportar datos entre distintos procesos. Se hace uso de la biblioteca Pydantic la cual se
encarga de llevar a cabo validación de datos, en este caso de JSON a clases de Python.
"""

class User(BaseModel):
    id: int
    email: str
    password: str
    admin: bool

    class Config:
        orm_mode = True


class Profile(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    user_id: int
    
    class Config:
        orm_mode = True    


class TouristDestination(BaseModel):
    """
        Clase que hereda de Base y hace referencía a un DTO de la información
        de los destinos turísticos.
    """
    id: int
    name: str
    description: str
    schedule: str
    fare: str
    contact: str
    recommendation: str
    difficulty: int
    latitude: float
    longitude: float
    hikes: str
    photos_path: str
    is_beach: bool
    is_forest: bool
    is_volcano: bool
    is_mountain: bool
    start_season: int
    end_season: int
    conservation_area_id: int

    class Config:
        orm_mode = True


class ConservationArea(BaseModel):
    """
        Clase que hereda de BaseModel y hace referencía a un DTO de la información de
        las áreas de conservación.
    """
    id: int
    name: str
    description: str
    photos_path: str
    region_path: str

    class Config:
        orm_mode = True

  

