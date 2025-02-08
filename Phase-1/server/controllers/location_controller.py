import json
from flask import jsonify, request
from models.location import Location
from extensions import db

def push_location():
    data = request.get_json() or {}
    device_id = data.get('device_id')
    coordinates = data.get('coordinates') or []
    if not device_id or not coordinates:
        return jsonify({'error': 'Invalid input'}), 400
    location_entry = Location.query.filter_by(device_id=device_id).first()
    if location_entry:
        stored_coordinates = json.loads(location_entry.coordinates)
        stored_coordinates.extend(coordinates)
        location_entry.coordinates = json.dumps(stored_coordinates)
    else:
        new_location = Location(device_id, coordinates)
        db.session.add(new_location)
    db.session.commit()
    return jsonify({'status': 'success'}), 200

def get_location(device_id):
    location_entry = Location.query.filter_by(device_id=device_id).first()
    if location_entry:
        return jsonify(location_entry.to_dict()), 200
    else:
        return jsonify({'error': 'Device not found'}), 404
