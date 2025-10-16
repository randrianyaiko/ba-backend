import os
from dotenv import load_dotenv
from app import create_app
from app.database import Base, engine
import app.models  # ensures all models are loaded
import awsgi
import logging

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Initialize database (if needed)
# -----------------------------
try:
    Base.metadata.create_all(engine)
    logger.info("All tables created successfully!")
except Exception as e:
    logger.exception("Database initialization failed.")

# -----------------------------
# Determine which service(s) to run
# -----------------------------
service_env = os.getenv("SERVICE")
service_names = [service_env] if service_env else ["auth", "products", "cart"]

# -----------------------------
# Create Flask app
# -----------------------------
app = create_app(service_names=service_names)

# -----------------------------
# Global error handler for Flask
# -----------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception in Flask route:")
    return {"message": "Internal Server Error"}, 500

# -----------------------------
# Event preprocessor for HTTP API v2.0
# -----------------------------
def preprocess_event(event):
    """
    Converts an API Gateway v2.0 HTTP API event into a proxy-format event for awsgi.
    """
    # If it's already a REST proxy event, return as-is
    if "httpMethod" in event:
        return event

    # Extract HTTP info from HTTP API v2.0 event
    http_info = event.get("requestContext", {}).get("http", {})
    method = http_info.get("method", "GET")
    path = http_info.get("path", "/")

    return {
        "httpMethod": method,
        "path": path,
        "headers": event.get("headers", {}),
        "queryStringParameters": event.get("queryStringParameters", {}),
        "body": event.get("body", None),
        "isBase64Encoded": event.get("isBase64Encoded", False),
        "requestContext": {
            "identity": {
                "sourceIp": http_info.get("sourceIp", ""),
                "userAgent": http_info.get("userAgent", "")
            }
        },
        "resource": path,
        "pathParameters": event.get("pathParameters", {}),
        "stageVariables": event.get("stageVariables", {})
    }

# -----------------------------
# Lambda handler
# -----------------------------
def lambda_handler(event, context):
    try:
        processed_event = preprocess_event(event)
        return awsgi.response(app, processed_event, context)
    except Exception as e:
        logger.exception("Error in Lambda handler:")
        return {
            "statusCode": 500,
            "body": f"Internal Server Error, {e}",
            "headers": {"Content-Type": "text/plain"}
        }
