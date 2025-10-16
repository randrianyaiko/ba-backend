from flask import Blueprint, request, jsonify
from app.utils.decorators import token_required
from app.services.activity import track_activity

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/activity/track', methods=['POST'])
@token_required
def track_activity_route(current_user):
    try:
        data = request.get_json()
        activity_type = data.get('activity_type')
        product_id = data.get('product_id')
        details = data.get('details', {})
        
        if not activity_type:
            return jsonify({'message': 'Activity type required'}), 400
        
        activity = track_activity(
            current_user['user_id'],
            activity_type,
            product_id,
            details
        )
        
        return jsonify({'message': 'Activity tracked successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500