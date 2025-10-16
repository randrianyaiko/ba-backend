# app/services/cart_service.py

from datetime import datetime
from app.models.cart import CartItem
from app.models.product import Product
from app.database import get_session


def get_cart(user_id: str):
    session = next(get_session())
    try:
        items = session.query(CartItem).filter(CartItem.user_id == user_id).all()

        cart_items = []
        total_items = 0

        for item in items:
            cart_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "name": item.product.name,
                "price": float(item.product.price),
                "image": item.product.image,
                "type": item.product.type
            })
            total_items += item.quantity

        return {"cart_items": cart_items, "total_items": total_items}
    finally:
        session.close()


def add_to_cart(user_id: str, product_id: str, quantity: int = 1):
    session = next(get_session())
    try:
        product = session.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return None

        cart_item = (
            session.query(CartItem)
            .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
            .first()
        )

        now = datetime.utcnow()
        if cart_item:
            cart_item.quantity += quantity
            cart_item.updated_at = now
        else:
            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                created_at=now,
                updated_at=now
            )
            session.add(cart_item)

        session.commit()
        return get_cart(user_id)
    finally:
        session.close()


def update_cart_quantity(user_id: str, product_id: str, change: int):
    session = next(get_session())
    try:
        cart_item = (
            session.query(CartItem)
            .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
            .first()
        )
        if not cart_item:
            return None

        cart_item.quantity += change
        if cart_item.quantity <= 0:
            session.delete(cart_item)
        else:
            cart_item.updated_at = datetime.utcnow()

        session.commit()
        return get_cart(user_id)
    finally:
        session.close()


def remove_from_cart(user_id: str, product_id: str):
    session = next(get_session())
    try:
        cart_item = (
            session.query(CartItem)
            .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
            .first()
        )
        if cart_item:
            session.delete(cart_item)
            session.commit()
    finally:
        session.close()

    return get_cart(user_id)


def clear_cart(user_id: str):
    session = next(get_session())
    try:
        session.query(CartItem).filter(CartItem.user_id == user_id).delete()
        session.commit()
    finally:
        session.close()

    return True
