from sqlalchemy import Integer, String, Column, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


"""
Se establecen los Objetos de acceso a datos (DAO), modelos los cuales son utilizados para almacenar
los datos que se almacenan en la base de datos. Se útiliza la biblioteca de Python sqlalchemy para 
realizar la conexión de los objetos con la base de datos.
"""

Base = declarative_base()


class User(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de los usuarios del sistema.
    """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    admin = Column(Boolean)


class Profile(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de los perfiles de los usuarios.
    """
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    profile_photo_path = Column(String)
    cover_photo_path = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)


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

    conservation_area = relationship(
        ConservationArea, backref="tourist_destinations")


class FavoriteArea(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de las áreas favoritas.
    """
    __tablename__ = "favorite_area"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    conservation_area_id = Column(
        Integer, ForeignKey("conservation_area.id"))

    user = relationship(User, backref="favorite_area")
    conservation_area = relationship(ConservationArea, backref="favorite_area")


class FavoriteDestination(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de los destinos favoritos.
    """
    __tablename__ = "favorite_destination"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    tourist_destination_id = Column(
        Integer, ForeignKey("tourist_destination.id"))

    user = relationship(User, backref="favorite_destination")
    tourist_destination = relationship(
        TouristDestination, backref="favorite_destination")


class VisitedDestination(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de los destinos visitados.
    """
    __tablename__ = "visited_destination"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    tourist_destination_id = Column(
        Integer, ForeignKey("tourist_destination.id"))

    user = relationship(User, backref="visited_destination")
    tourist_destination = relationship(
        TouristDestination, backref="visited_destination")


class Review(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de las opiniones.
    """
    __tablename__ = "review"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    text = Column(String)
    date = Column(DateTime)
    calification = Column(Integer)
    image_path = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    tourist_destination_id = Column(
        Integer, ForeignKey("tourist_destination.id"))
    
    user = relationship(User, backref="review")
    tourist_destination = relationship(TouristDestination, backref="review")

    
class Gallery(Base):
    """
        Clase que hereda de Base y hace referencía a un DAO de la información
        de las galerias de los usuarios.
    """
    __tablename__ = "gallery"
    id = Column(Integer, primary_key=True, index=True)
    photos_path = Column(String)
    
    profile_id = Column(Integer, ForeignKey("profile.id"))
    profile = relationship(Profile)

