from pydantic import BaseModel

"""
Se establecen los objetos de de transferencia de datos (DTO), esquemas que son utilizados para
transportar datos entre distintos procesos. Se hace uso de la biblioteca Pydantic la cual se
encarga de llevar a cabo validación de datos, en este caso de JSON a clases de Python.
"""


class ConservationArea(BaseModel):
    """
        Clase que hereda de BaseModel y hace referencía a un DTO de la información de
        las áreas de conservación.
    """
    name: str
    description: str
    photos_path: str
    region_path: str

    class Config:
        orm_mode = True

