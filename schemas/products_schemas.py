from pydantic import  BaseModel


class ProductBase(BaseModel):
    name: str
    price: float
    country: str