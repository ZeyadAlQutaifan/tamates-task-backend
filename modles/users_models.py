from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # Increased from 100 to 255
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="User")
    registered_on = Column(String, nullable=False)