import requests

# URL of the API.
url = "http://localhost:5000/process_image"

# File path for the image you want to test (inside the testimages folder).
image_path = "testimages/image.png"

# Placeholder variables to send.
data = {
    "Name": "Md. Monjurul Ahasan",
    "Date of Birth": "15 Nov 1964"
}

with open(image_path, "rb") as f:
    files = {"image": f}
    response = requests.post(url, data=data, files=files)

print(response.json())