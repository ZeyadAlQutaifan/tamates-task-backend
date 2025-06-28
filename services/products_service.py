from sqlalchemy.orm import Session
from modles.product_models import Product
from schemas.products_schemas import ProductBase
from fastapi import HTTPException

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_product_by_id(self, product_id: int):
        product = self.db.query(Product).get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def get_products(self, page: int = 0, per_page: int = 10):
        return self.db.query(Product).offset(page).limit(per_page).all()

    def create_product(self, product_data: ProductBase):
        new_product = Product(
            name=product_data.name,
            country=product_data.country,
            price=product_data.price
        )
        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        return new_product
