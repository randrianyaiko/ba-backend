import os
from dotenv import load_dotenv
from app import create_app
from app.database import Base, engine
import app.models  # ensures all models are loaded

load_dotenv()

# Initialize database (only if needed)
Base.metadata.create_all(engine)
print("All tables created successfully!")

# Determine which service(s) to run
# SERVICE can be: "auth", "products", "cart", "recommendation"
service_env = os.getenv("SERVICE")
service_names = [service_env] if service_env else None

# Create Flask app with selected service(s)
app = create_app(service_names=service_names)

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True") == "True"
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
