from flask import Blueprint
from controllers.location_controller import push_location, get_location

location_routes = Blueprint('location_routes', __name__)
location_routes.add_url_rule('/push_location', view_func=push_location, methods=['POST'])
location_routes.add_url_rule('/get_location/<device_id>', view_func=get_location, methods=['GET'])
