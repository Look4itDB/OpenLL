import sys
sys.dont_write_bytecode = True
from flask import Flask
from config import Config
from extensions import db
from routes.location_routes import location_routes
from services.logging_service import configure_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    configure_logging(app)
    db.init_app(app)
    app.register_blueprint(location_routes)
    with app.app_context():
        db.create_all()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
