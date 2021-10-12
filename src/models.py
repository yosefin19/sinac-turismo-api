
from sqlalchemy import Integer, String, Column, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


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


class TouristDestination(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de las áreas de conservación.
    """
    __tablename__ = "tourist_destination"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    schedule = Column(String)
    fare = Column(String)
    contact = Column(String)
    recommendation = Column(String)
    difficulty = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    hikes = Column(String)
    photos_path = Column(String)
    is_beach = Column(Boolean)
    is_forest = Column(Boolean)
    is_volcano = Column(Boolean)
    is_mountain = Column(Boolean)
    start_season = Column(Integer)
    end_season = Column(Integer)
    conservation_area_id = Column(Integer, ForeignKey("conservation_area.id"))

    conservation_area = relationship(ConservationArea, backref="tourist_destinations")


