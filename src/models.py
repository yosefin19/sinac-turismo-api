from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(Base):
    __tablename__= "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)


class Profile(Base):
    __tablename__= "profile"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(Integer)
    email = Column(String)
    admin = Column(Boolean)
     
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)
