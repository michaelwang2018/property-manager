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

@app.route('/generate_rental_ad', methods=['POST'])
def generate_rental_ad():
    data = request.get_json()
    
    # Extracting information from the request
    files = data.get("images", [])
    contact_name = data.get("contact_name", "Emilia")
    contact_email = data.get("contact_email", "yoland@rentaigent")
    agency_name = data.get("agency_name", "AI Rental Agency")
    location = data.get("location", "Tacoma, Washington")
    security_deposit = data.get("security_deposit", "two months")
    
    # Prepare images as Part objects
    images = [Part.from_uri(url, mime_type="image/jpeg") for url in files]
    
    # Prepare the prompt
    prompt = f"""
      Look at the pictures uploaded and go through them in detail and describe it in such a way renters love to see the house.
      Use the rent amount based on prevailing market condition at this location {location}. Use current date plus 10 days as available date for now.
      Use liberty to use general rental ads information while generating the text.
      Use security deposit as {security_deposit}.
      Use contact name as {contact_name} and use email for references: {contact_email}.
      Your name is {agency_name}.
      Questions:
      - Generate rental post ad for the house shown in the pictures.
    """

    contents = images + [prompt]

    # Generate content
    try:
        response = model.generate_content(contents)
        return jsonify({"ad_text": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
