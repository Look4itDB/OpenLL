# import libraries
# initilasing the flask app
# db connection and schema
# create endpoint (to receive location data: device_id, latitude, longitude)

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


def init_db():
    connection = sqlite3.connect('location_data.db')
    c = connection.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS location (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            latitude REAL,
            longitude REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()


@app.route('/push-location', methods=['POST'])
def push_location():
    """
    Expects JSON:
    {
      "device_id": "047",
      "latitude": 12.34567,
      "longitude": 76.54321
    }
    """
    data = request.get_json() or {}
    device_id = data.get('device_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([device_id, latitude, longitude]):
        return jsonify({'error': 'Missing field'}), 400 

    connection = sqlite3.connect('location_data.db')
    c = connection.cursor()
    c.execute('''
        INSERT INTO location (device_id, latitude, longitude)
        VALUES (?, ?, ?)
    ''', (device_id, latitude, longitude))
    connection.commit()
    connection.close()

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    init_db() 
    app.run(debug=True, host='0.0.0.0', port=5000)
