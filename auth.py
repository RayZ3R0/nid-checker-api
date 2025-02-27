from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from decouple import config

auth = HTTPBasicAuth()

# Get API credentials from environment variables or use defaults
API_USERNAME = config('API_USERNAME', default='admin')
API_PASSWORD = config('API_PASSWORD', default='password')

users = {
    API_USERNAME: generate_password_hash(API_PASSWORD)
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None