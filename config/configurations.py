import os
import sys
import redis

sys.path.append(os.getcwd())

# LOGS DIR
LOG_DIR = os.environ.get('LOG_DIR')
CLIENT_SECRETS_FILE = os.environ.get('CLIENT_SECRETS_FILE')
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

SECRET_KEY = os.environ.get('SECRET_KEY')

FLASK_APP = os.environ.get('FLASK_APP')
# FLASK_ENV = os.environ.get('FLASK_ENV')

# Flask-Session
SESSION_TYPE = os.environ.get('SESSION_TYPE')
SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS'))

# initial timestamp
INITIAL_TIMESTAMP = os.environ.get('INITIAL_TIMESTAMP')

# Redis
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PWD = os.environ.get('REDIS_PWD')
REDIS_DB = os.environ.get('REDIS_DB')


# MongoDb
MONGO_URI = os.environ.get('MONGO_URI')
MONGO_PWD = os.environ.get('MONGO_PWD')
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_COLLECTION = os.environ.get('MONGO_COLLECTION')
