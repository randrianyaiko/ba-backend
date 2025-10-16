from flask import Flask
from flask_cors import CORS
from app.config import Config

# List of allowed CORS origins
CORS_ORIGINS = Config.CORS_ORIGINS

BLUEPRINTS = {
    "auth": ("app.routes.auth", "auth_bp"),
    "products": ("app.routes.products", "products_bp"),
    "cart": ("app.routes.cart", "cart_bp"),
    "recommendation": ("app.routes.recommendation", "recommendation_bp")
}

def create_app(service_names=None):
    """
    Generic app factory.
    
    :param service_names: List of services to include. 
                          If None, include all services (full app).
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object("app.config.Config")
    
    # Initialize extensions
    CORS(app, origins=CORS_ORIGINS)
    
    # Determine which services to register
    if service_names is None:
        services_to_register = BLUEPRINTS.keys()
    else:
        services_to_register = service_names
    
    # Dynamically import and register blueprints
    for service in services_to_register:
        module_path, bp_name = BLUEPRINTS[service]
        module = __import__(module_path, fromlist=[bp_name])
        blueprint = getattr(module, bp_name)
        app.register_blueprint(blueprint, url_prefix="/api")
    
    return app
