# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI',
        'postgresql://user_for_apache_kafka_project:apache_kafka@localhost/location_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Set to False in production
