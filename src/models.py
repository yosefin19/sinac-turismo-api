from sqlalchemy import Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base


"""
Se establecen los Objetos de acceso a datos (DAO), modelos los cuales son utilizados para almacenar
los datos que se almacenan en la base de datos. Se útiliza la biblioteca de Python sqlalchemy para 
realizar la conexión de los objetos con la base de datos.
"""


Base = declarative_base()


class ConservationArea(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de las áreas de conservación.
    """
    __tablename__ = "conservation_area"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    photos_path = Column(String)
    region_path = Column(String)

