import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ----------------------------
    # Environment
    # ----------------------------
    ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

    # ----------------------------
    # Secrets
    # ----------------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # ----------------------------
    # Database / SQLAlchemy
    # ----------------------------
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    # ----------------------------
    # AWS Configuration local
    # ----------------------------
    # Always define attributes to avoid AttributeError
    
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") if ENVIRONMENT == "local" else None
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") if ENVIRONMENT == "local" else None
    AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL") if ENVIRONMENT == "local" else None
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN")
    AWS_SQS_QUEUE_ARN = os.getenv("AWS_SQS_QUEUE_ARN")

    # ----------------------------
    # Qdrant
    # ----------------------------
    QDRANT_HOST = os.getenv("QDRANT_URL")
    QDRANT_PORT = os.getenv("QDRANT_PORT")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
    