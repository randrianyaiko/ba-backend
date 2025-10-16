from datetime import datetime
from sqlalchemy import or_
from app.models.product import Product
from app.database import get_session
from app.services.activity import track_activity
import uuid

def create_product(product_data, user_id=None):
    session = next(get_session())
    try:
        product_id = str(uuid.uuid4())
        now = datetime.utcnow()

        product = Product(
            product_id=product_data['id'],
            name=product_data['name'],
            description=product_data.get('description', ''),
            price=product_data['price'],
            image=product_data.get('image', ''),
            type=product_data['type'],
            category=product_data.get('category', product_data['type']),
            created_at=now,
            updated_at=now
        )
        
        session.add(product)
        session.commit()
        session.refresh(product)

        track_activity(user_id, "CREATE_PRODUCT", product_data['id'], product.to_dict())
        return product
    finally:
        session.close()

def get_products_by_ids(product_ids, search_query=None, category=None):
    """
    Fetch products by a list of IDs, optionally filtered by search/category.
    Sorted according to `product_ids`.
    """
    if not product_ids:
        return []

    session = next(get_session())
    try:
        query = session.query(Product).filter(Product.product_id.in_(product_ids))

        if category and category.lower() != 'all':
            query = query.filter(Product.category == category)

        if search_query:
            pattern = f"%{search_query}%"
            query = query.filter(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern)
                )
            )

        products = query.all()
        product_dict = {p.product_id: p.to_dict() for p in products}
        sorted_products = [product_dict[i] for i in product_ids if i in product_dict]

        return sorted_products
    finally:
        session.close()

def get_product(product_id: str):
    session = next(get_session())
    try:
        return session.query(Product).filter(Product.product_id == product_id).first()
    finally:
        session.close()

def get_products(page=1, per_page=6, search_query=None, category=None, exclude_ids=None):
    """
    Fetch products with optional pagination, search, category filter, and exclude certain IDs.
    """
    session = next(get_session())
    try:
        query = session.query(Product)

        if category and category.lower() != 'all':
            query = query.filter(Product.category == category)

        if search_query:
            pattern = f"%{search_query}%"
            query = query.filter(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern)
                )
            )

        if exclude_ids:
            query = query.filter(~Product.product_id.in_(exclude_ids))

        total_items = query.count()
        products = (
            query.order_by(Product.created_at.desc())
                 .offset((page - 1) * per_page)
                 .limit(per_page)
                 .all()
        )

        return {
            'products': [p.to_dict() for p in products],
            'total_pages': (total_items + per_page - 1) // per_page,
            'current_page': page,
            'total_items': total_items
        }
    finally:
        session.close()


def full_scan_products():
    """Fetch all products without pagination (not recommended for huge tables)."""
    session = next(get_session())
    try:
        products = session.query(Product).all()
        return [product.to_dict() for product in products]
    finally:
        session.close()
