from flask import Flask, request, jsonify
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part

app = Flask(__name__)

# Use the environment variable if the user doesn't provide Project ID.
GOOGLE_APPLICATION_CREDENTIALS = "gcp_service_key.json"
PROJECT_ID = "vivid-argon-440517-e8"
if not PROJECT_ID or PROJECT_ID == "[your-project-id]":
    PROJECT_ID = str(os.environ.get("GOOGLE_CLOUD_PROJECT"))

LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

vertexai.init(project=PROJECT_ID, location=LOCATION)

MODEL_ID = "gemini-1.5-flash-002"
model = GenerativeModel(MODEL_ID)

@app.route('/generate_listing_details', methods=['POST'])
def generate_listing_details():
    data = request.get_json()
    
    # Extracting information from the request
    files = data.get("images", ["https://photos.zillowstatic.com/fp/0b9eceb0c092f9373978518faaf62aa5-cc_ft_1536.webp", "https://photos.zillowstatic.com/fp/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.webp", "https://photos.zillowstatic.com/fp/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.webp", "https://photos.zillowstatic.com/fp/362e91b537ea78f33ae2bbab1561edb7-cc_ft_768.webp", "https://photos.zillowstatic.com/fp/ccc608cdc87b07ffb26294fb10acff68-cc_ft_1536.webp", "https://photos.zillowstatic.com/fp/1a9856a80e2dbaac9672cfb0b6efcbad-cc_ft_768.webp", "https://photos.zillowstatic.com/fp/0278b53e7763004a2c8235006c90dd9c-cc_ft_768.webp"])
    address = data.get("address", "3249 17th St #2, san francisco, CA 94110")
    contact_name = data.get("contact_name", "Emilia")
    # contact_email = data.get("contact_email", "yoland@rentaigent")
    # agency_name = data.get("agency_name", "AI Rental Agency")
    # location = data.get("location", "Tacoma, Washington")
    security_deposit = data.get("security_deposit", "two months")
    rent = data.get("rent", "1200")
    
    # Prepare images as Part objects
    images = [Part.from_uri(url, mime_type="image/jpeg") for url in files]
    
    # Updated prompt to request structured data
    prompt = f"""
      Analyze the provided images and generate a rental listing with the following specifications:
      - Location: {address}
      - Security deposit: {security_deposit}
      - Rent: {rent}
      - Contact: {contact_name}

      Return the response in the following JSON format:
      {{
        "address": "{address}",
        "bedrooms": <number>,
        "bathrooms": <float>,
        "square_feet": <number>,
        "monthly_rent": <number based on market conditions>,
        "security_deposit": <number based on market conditions>,
        "pets_allowed": <"Yes" or "No">,
        "laundry_type": <"In-Unit", "On-Site", or "None">,
        "air_conditioning": <"Central", "Window Unit", or "None">,
        "parking_type": <"Covered", "Street", "Garage", or "None">,
        "heating": <"Central", "Electric", "Gas", or "None">,
        "shared_property": <"Yes" or "No">,
        "bathroom_type": <"Private" or "Shared">,
        "description": <detailed property description>,
        "message": <friendly response to user>
      }}

      Base all details on the images provided and current market conditions.
    """

    contents = images + [prompt]

    # Generate content
    try:
        response = model.generate_content(contents)
        return response.text  # This will now return JSON-formatted string
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
