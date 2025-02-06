import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import json

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_for_apache_kafka_project:apache_kafka@localhost/location_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure file-only logging (no console output)
log_handler = logging.FileHandler("logFile.txt", mode='a')
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

# Remove default Flask logging to console
app.logger.handlers = []  # Clear existing handlers
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

# Global log counter
log_counter = 1

# Define the Location model
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    coordinates = db.Column(JSON, nullable=False)

    def __init__(self, device_id, coordinates):
        self.device_id = device_id
        self.coordinates = json.dumps(coordinates)

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "coordinates": json.loads(self.coordinates)
        }

# Initialize database tables
with app.app_context():
    db.create_all()

@app.before_request
def log_request():
    """Log each incoming request with index."""
    global log_counter
    request_data = request.get_json() if request.is_json else 'No JSON'
    request_log = f"{log_counter} | REQUEST: {request.method} {request.path} | IP: {request.remote_addr} | Data: {request_data}"
    
    # Store the log index in request context
    request.environ['log_index'] = log_counter
    
    # Increment log counter for next request
    log_counter += 1

    app.logger.info(request_log)

@app.after_request
def log_response(response):
    """Log response on the same line as request."""
    log_index = request.environ.get('log_index', 'Unknown')
    response_log = f"{log_index} | RESPONSE: {response.status_code}"
    app.logger.info(response_log)
    return response

@app.route('/push_location', methods=['POST'])
def push_location():
    data = request.get_json() or {}
    device_id = data.get('device_id')
    coordinates = data.get('coordinates') or []

    if not device_id or not coordinates or not isinstance(coordinates, list):
        return jsonify({'error': 'Invalid input'}), 400

    location_entry = Location.query.filter_by(device_id=device_id).first()

    if location_entry:
        stored_coordinates = json.loads(location_entry.coordinates)
        stored_coordinates.extend(coordinates)
        location_entry.coordinates = json.dumps(stored_coordinates)
    else:
        db.session.add(Location(device_id, coordinates))

    db.session.commit()
    return jsonify({'status': 'success'}), 200

@app.route('/get_location/<device_id>', methods=['GET'])
def get_location(device_id):
    location_entry = Location.query.filter_by(device_id=device_id).first()
    return jsonify(location_entry.to_dict()) if location_entry else jsonify({'error': 'Device not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
