#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

# Load token from .env
load_dotenv()
token = os.getenv("AUTH_TOKEN")

print(f"Token from .env: {token}")
print(f"Token length: {len(token)}")
print(f"Token hex representation: {' '.join(hex(ord(c)) for c in token)}")

# Make a simple GET request to test authentication
url = "http://localhost:5000/"
headers = {"X-API-Token": token}

print(f"\nSending request with token...")
response = requests.get(url, headers=headers)

print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")