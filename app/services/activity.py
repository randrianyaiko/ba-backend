from src.messaging.sns import SNSMessenger
from app.models.activity import Activity
from app.config import Config
import uuid
from datetime import datetime
import json

messenger = SNSMessenger(
    sns_topic_arn=Config.AWS_SNS_TOPIC_ARN,
    sqs_queue_arn=Config.AWS_SQS_QUEUE_ARN,
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION,
    endpoint_url=Config.AWS_ENDPOINT_URL,
    )

# -------------------------
# Track activity (send to Kafka)
# -------------------------
def track_activity(user_id, activity_type, product_id=None, details=None):
    activity_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    activity_item = {
        'activity_id': activity_id,
        'user_id': user_id,
        'activity_type': activity_type,
        'product_id': product_id,
        'details': details,
        'created_at': created_at
    }
    
    messenger.send_message(message=json.dumps(activity_item), subject="User Activity")

    return Activity(**activity_item)
