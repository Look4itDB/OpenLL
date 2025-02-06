from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import json

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_for_apache_kafka_project:apache_kafka@localhost/location_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
