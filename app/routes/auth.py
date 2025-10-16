from flask import Blueprint, request, jsonify
from app.services.auth import create_user, get_user_by_email, verify_password, generate_token
from app.utils.decorators import token_required
from app.services.activity import track_activity
from app.config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not email or not name or not password:
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409
        
        # Create user
        user = create_user(email, name, password)
        
        # Generate token
        token = generate_token(user, Config.JWT_SECRET_KEY)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password required'}), 400
        
        # Get user by email
        user = get_user_by_email(email)
        if not user or not verify_password(user, password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user, Config.JWT_SECRET_KEY)
        track_activity(user.user_id, "LOGIN")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/protected_resource', methods=['GET'])
@token_required
def protected_resource(current_user):
    return jsonify({
        'message': 'This is a protected resource',
        'user_email': current_user['email']
    }), 200