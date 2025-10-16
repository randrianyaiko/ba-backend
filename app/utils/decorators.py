import jwt
from flask import request, jsonify
from app.services.auth import get_user_by_id
from app.config import Config
from functools import wraps
from flask import request, jsonify
from app.services.auth import get_user_by_id


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
            kwargs['current_user'] = current_user.to_dict()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def verify_token(token):
    """
    Verifies a JWT token and returns the current_user dict if valid.
    Raises an exception if token is invalid or expired.
    """
    data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
    current_user = get_user_by_id(data['user_id'])
    if not current_user:
        raise Exception('Invalid token')
    return current_user.to_dict()

def token_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in the header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(" ")[1]
            except IndexError:
                pass  # Invalid token format, but we'll continue without it
        
        # If token exists, try to decode it
        if token:
            try:
                data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
                request.current_user = data
            except jwt.ExpiredSignatureError:
                # Token is expired, but we'll continue without it
                pass
            except jwt.InvalidTokenError:
                # Invalid token, but we'll continue without it
                pass
        
        # If no token or invalid token, set current_user to None
        if not hasattr(request, 'current_user'):
            request.current_user = None
            
        return f(*args, **kwargs)
    return decorated