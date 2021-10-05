from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(Base):
    __tablename__= "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)

