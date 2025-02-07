# app/controllers/location_controller.py
import json
from flask import Blueprint, request, jsonify, current_app
from app.models.location import Location
from app import db

location_bp = Blueprint('location', __name__)

# Global log counter
log_counter = 1

@location_bp.before_app_request
def log_request():
    global log_counter
    request_data = request.get_json() if request.is_json else 'No JSON'
    log_index = log_counter
    # Store the log index in the request environment
    request.environ['log_index'] = log_index

    log_message = (
        f"{log_index} | REQUEST: {request.method} {request.path} | "
        f"IP: {request.remote_addr} | Data: {request_data}"
    )
    current_app.logger.info(log_message)
    log_counter += 1

@location_bp.after_app_request
def log_response(response):
    log_index = request.environ.get('log_index', 'Unknown')
    response_log = f"{log_index} | RESPONSE: {response.status_code}"
    current_app.logger.info(response_log)
    return response

@location_bp.route('/push_location', methods=['POST'])
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
        new_location = Location(device_id, coordinates)
        db.session.add(new_location)

    db.session.commit()
    return jsonify({'status': 'success'}), 200

@location_bp.route('/get_location/<device_id>', methods=['GET'])
def get_location(device_id):
    location_entry = Location.query.filter_by(device_id=device_id).first()
    if location_entry:
        return jsonify(location_entry.to_dict()), 200
    else:
        return jsonify({'error': 'Device not found'}), 404
