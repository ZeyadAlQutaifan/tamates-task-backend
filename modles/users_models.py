from sqlalchemy import  Boolean, Column, ForeignKey, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hashed = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="User")
    registered_on = Column(String, nullable=False)