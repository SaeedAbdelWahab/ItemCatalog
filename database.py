import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
 
Base = declarative_base()




class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

 
class Category(Base):
    __tablename__ = 'Category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

 
class Item(Base):
    __tablename__ = 'Item'


    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    category_id = Column(Integer,ForeignKey('Category.id'))
    category = relationship(Category) 

    @property
    def serialize(self):
       
       return {
           'name'         : self.name,
           'description'         : self.description,
           'id'         : self.id,
       }
 

engine = create_engine('sqlite:///CatalogApp.db')
 

Base.metadata.create_all(engine)
