from sqlalchemy import  Boolean, Column, ForeignKey, Integer, String, Float
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    price = Column(Float)
    description = Column(String)
    location = Column(String)