import json
from extensions import db

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    coordinates = db.Column(db.JSON, nullable=False)
    def __init__(self, device_id, coordinates):
        self.device_id = device_id
        self.coordinates = json.dumps(coordinates)
    def to_dict(self):
        return {"device_id": self.device_id, "coordinates": json.loads(self.coordinates)}
