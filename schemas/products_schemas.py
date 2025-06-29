from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    price: float
    location: str


class ProductResponse(BaseModel):
    """
    Product response model
    """
    id: int = Field(..., description="Product ID", example=1)
    title: str = Field(..., description="Product title", example="Sword of Valor")
    description: str = Field(..., description="Product description", example="A legendary sword with magical powers")
    price: float = Field(..., description="Product price", example=150.00)
    location: str = Field(..., description="Product location", example="JO")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Sword of Valor",
                "description": "A legendary sword with magical powers",
                "price": 150.00,
                "location": "JO"
            }
        }