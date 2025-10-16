from datetime import datetime
import uuid
from app.database import get_session
from app.models.order import Order


def create_order(user_id: str, product_id: str, quantity: int = 1, status: str = "pending"):
    session = next(get_session())
    try:
        now = datetime.now()

        # Optional: prevent duplicate pending orders for same user/product
        existing_order = session.query(Order).filter(
            Order.user_id == user_id,
            Order.product_id == product_id,
            Order.status == status
        ).first()

        if existing_order:
            existing_order.quantity += quantity
            existing_order.updated_at = now
            session.commit()
            session.refresh(existing_order)
            return existing_order.to_dict()

        # Otherwise create a new order
        order = Order(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            status=status,
            created_at=now,
            updated_at=now
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return order.to_dict()
    finally:
        session.close()


def get_orders_by_user(user_id: str):
    session = get_session()
    try:
        orders = session.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
        return [o.to_dict() for o in orders]
    finally:
        session.close()
