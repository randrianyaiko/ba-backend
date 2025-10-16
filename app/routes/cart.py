from flask import Blueprint, request, jsonify
from app.services.cart import get_cart, add_to_cart, update_cart_quantity, remove_from_cart, clear_cart
from app.utils.decorators import token_required
from app.services.activity import track_activity
from app.services.order import create_order

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart', methods=['GET'])
@token_required
def get_cart_route(current_user):
    try:
        cart = get_cart(current_user['user_id'])
        return jsonify(cart), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cart_bp.route('/cart/add', methods=['POST'])
@token_required
def add_to_cart_route(current_user):
    try:
        data = request.get_json()
        product_id = data.get('productId')
        quantity = data.get('quantity', 1)

        if not product_id:
            return jsonify({'message': 'Product ID required'}), 400

        result = add_to_cart(current_user['user_id'], product_id, quantity)
        track_activity(current_user['user_id'], 'ADD_TO_CART', product_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cart_bp.route('/cart/update_quantity', methods=['POST'])
@token_required
def update_cart_quantity_route(current_user):
    try:
        data = request.get_json()
        product_id = data.get('productId')
        change = data.get('change')

        if not product_id or change is None:
            return jsonify({'message': 'Product ID and change required'}), 400
        result = update_cart_quantity(current_user['user_id'], product_id, change)        
        track_activity(current_user['user_id'], 'UPDATE_CART_QUANTITY', product_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cart_bp.route('/cart/remove', methods=['POST'])
@token_required
def remove_from_cart_route(current_user):
    try:
        data = request.get_json()
        product_id = data.get('productId')

        if not product_id:
            return jsonify({'message': 'Product ID required'}), 400

        result = remove_from_cart(current_user['user_id'], product_id)
        track_activity(current_user['user_id'], 'REMOVE_FROM_CART', product_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cart_bp.route('/checkout', methods=['POST'])
@token_required
def checkout_route(current_user):
    try:
        user_id = current_user['user_id']
        cart = get_cart(user_id)

        if not cart['cart_items']:
            return jsonify({'message': 'Cart is empty'}), 400

        # Copy cart items to avoid losing them when clearing
        cart_items = cart['cart_items'].copy()

        # Clear the cart first to prevent duplicate order creation
        clear_cart(user_id)

        # Create an order for each item in the cart
        created_orders = []
        for item in cart_items:
            order = create_order(
                user_id=user_id,
                product_id=item['product_id'],
                quantity=item['quantity']
            )
            # Ensure the order is returned as a dict
            if hasattr(order, "to_dict"):
                order_data = order.to_dict()
            else:
                order_data = order
            created_orders.append(order_data)
            track_activity(user_id, 'ORDER', item['product_id'])
        
        return jsonify({
            'message': 'Checkout successful',
            'orders': created_orders
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
