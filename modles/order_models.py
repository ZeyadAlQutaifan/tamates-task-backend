from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Float

from database import Base
from modles.product_models import Product
from modles.users_models import User


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    trx_number = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class PaymentRequest(Base):
    __tablename__ = 'payment_request'
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    reference_id = Column(Integer, ForeignKey(Order.id), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    redirect_url = Column(String, nullable=False)
    callback_url = Column(String, nullable=False)