# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .logging_config import configure_logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Configure logging
    configure_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register controllers blueprint
    from .controllers.location_controller import location_bp
    app.register_blueprint(location_bp)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
