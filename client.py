import argparse
import json
import os
import time
from pathlib import Path
import requests
from decouple import config


def send_image_to_ocr(image_path, server_url=None, auth_token=None, name=None, dob=None):
    """
    Send an image to the OCR API and get the extracted information.
    """
    # Default server URL if not provided
    if not server_url:
        server_url = "http://localhost:5000/process_image"
    
    # Get auth token from .env if not provided
    if not auth_token:
        auth_token = config('AUTH_TOKEN', default='').strip()
    
    # Prepare headers with authentication
    headers = {
        "X-API-Token": auth_token
    }
    
    # Prepare form data if comparison info provided
    form_data = {}
    if name:
        form_data["Name"] = name
    if dob:
        form_data["Date of Birth"] = dob
    
    # Check if image exists
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    print(f"Sending image: {image_path}")
    print(f"Server URL: {server_url}")
    print(f"Headers: X-API-Token: '{auth_token}'")
    
    # Send the request
    start_time = time.time()
    try:
        with open(image_path, 'rb') as image_file:
            files = {
                'image': (image_path.name, image_file, f'image/{image_path.suffix[1:]}')
            }
            response = requests.post(
                server_url,
                headers=headers,
                files=files,
                data=form_data
            )
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to the server at {server_url}")
        print("   Make sure your Flask application is running.")
        return None
    except Exception as e:
        print(f"❌ Error sending request: {e}")
        return None
    
    elapsed_time = time.time() - start_time
    
    # Check response
    if response.ok:
        try:
            result = response.json()
            
            # Print results in a structured format
            print("\n✅ Successfully processed image!")
            print(f"⏱️  Processing time: {elapsed_time:.2f} seconds")
            
            # Print the full raw JSON for debugging
            print("\n[DEBUG] Full JSON response:")
            print(json.dumps(result, indent=2))
            
            print("\n📋 Extracted Information:")
            
            # Print main extracted data safely
            print(f"👤 Name: {result.get('Name', 'Not in response')}")
            print(f"🎂 Date of Birth: {result.get('Date of birth', 'Not in response')}")
            print(f"🆔 ID Number: {result.get('ID Number', 'Not in response')}")
            
            # Print similarity scores if available
            if "similarity" in result:
                print("\n🔍 Similarity Analysis:")
                print(json.dumps(result["similarity"], indent=2))
            
            return result
            
        except json.JSONDecodeError:
            print(f"❌ Error: Server did not return valid JSON")
            print(f"Response: {response.text}")
            return None
    else:
        print(f"❌ Error {response.status_code}: {response.reason}")
        try:
            error_data = response.json()
            print(f"Server message: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"Response: {response.text}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the NID OCR API")
    parser.add_argument("--image", "-i", default="testimages/image.png", 
                      help="Path to the image file (default: testimages/image.png)")
    parser.add_argument("--url", "-u", default="http://localhost:5000/process_image",
                      help="URL of the OCR server (default: http://localhost:5000/process_image)")
    parser.add_argument("--token", "-t", default=None,
                      help="Authentication token (default: from .env file)")
    parser.add_argument("--name", "-n", default=None,
                      help="Name to compare with extracted data")
    parser.add_argument("--dob", "-d", default=None,
                      help="Date of birth to compare with extracted data")
    
    args = parser.parse_args()
    
    # Make sure testimages directory exists
    os.makedirs(os.path.dirname(args.image), exist_ok=True)
    
    # Send image to OCR service
    result = send_image_to_ocr(
        image_path=args.image,
        server_url=args.url,
        auth_token=args.token,
        name=args.name,
        dob=args.dob
    )
    
    # Write result to file for later analysis
    if result:
        with open("ocr_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\nResults saved to ocr_result.json")