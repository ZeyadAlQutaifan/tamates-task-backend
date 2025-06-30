from sqlalchemy.orm import Session
from modles.product_models import Product
from schemas.products_schemas import ProductResponse
from schemas.api_response_schemas import PaginatedResponse


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        """
        Get a single product by ID
        """
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        return ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            price=product.price,
            location=product.location
        )


    def get_products(self, page: int = 1, size: int = 10, location: str = None) -> PaginatedResponse[ProductResponse]:
        """
        Get paginated list of products
        """
        # Calculate offset (page starts from 1)
        offset = (page - 1) * size

        # Base query
        query = self.db.query(Product)

        # Apply location filter if provided and not empty
        if location and location.strip():
            query = query.filter(Product.location == location.strip())

        # Get products with pagination
        products = (query
                    .offset(offset)
                    .limit(size)
                    .all())

        # Get total count with same filter
        count_query = self.db.query(Product)
        if location and location.strip():
            count_query = count_query.filter(Product.location == location.strip())

        total_count = count_query.count()

        # Calculate pagination info
        total_pages = (total_count + size - 1) // size
        has_next = page < total_pages
        has_previous = page > 1

        # Convert to response format
        product_responses = [
            ProductResponse(
                id=product.id,
                title=product.title,
                description=product.description,
                price=product.price,
                location=product.location
            )
            for product in products
        ]

        return PaginatedResponse[ProductResponse](
            content=product_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
