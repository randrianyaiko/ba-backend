import os
import base64
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
    Converts an API Gateway v2.0 HTTP API event into a REST-style proxy event for awsgi.
    """
    # Already REST proxy (API Gateway v1.0)
    if "httpMethod" in event:
        return event

    # HTTP API v2.0
    http_info = event.get("requestContext", {}).get("http", {})
    method = http_info.get("method", "GET")
    path = http_info.get("path", "/")

    # Headers and query parameters
    headers = event.get("headers") or {}
    query_params = event.get("queryStringParameters") or {}
    path_params = event.get("pathParameters") or {}

    # Body handling (decode if Base64)
    body = event.get("body")
    if body and event.get("isBase64Encoded", False):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except Exception as e:
            logger.warning(f"Failed to decode Base64 body: {e}")
            body = None

    return {
        "httpMethod": method,
        "path": path,
        "headers": headers,
        "queryStringParameters": query_params,
        "body": body,
        "isBase64Encoded": False,
        "requestContext": {
            "identity": {
                "sourceIp": http_info.get("sourceIp", ""),
                "userAgent": http_info.get("userAgent", "")
            }
        },
        "resource": path,
        "pathParameters": path_params,
        "stageVariables": event.get("stageVariables") or {}
    }

# -----------------------------
# Lambda handler
# -----------------------------
def lambda_handler(event, context):
    try:
        processed_event = preprocess_event(event)
        response = awsgi.response(app, processed_event, context)
        return response
    except Exception as e:
        logger.exception("Error in Lambda handler:")
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {str(e)}",
            "headers": {"Content-Type": "text/plain"}
        }
