import base64
from threading import Thread
from typing import Union
from fastapi import FastAPI, HTTPException
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
from vertexai.preview.prompts import Prompt


# import weave
# client = weave.init("hallovenkata-picarro/my-project")
# call = client.get_call("0192f1ea-e540-78e3-b736-9cb7213d3822")
system_prompt = """Act as a Property Management Advisor. Your task is to create a highly attractive online rental advertisement targeted at future tenants. This advertisement will be used on platforms like Facebook Marketplace.

You must return your response in the following JSON format:
{
    "address": "<full property address>",
    "bedrooms": <number>,
    "bathrooms": <number>,
    "rent": "<monthly rent with $ symbol>",
    "amenities": [
        "<amenity 1>",
        "<amenity 2>",
        "..."
    ],
    "lease_terms": "<lease terms>",
    "contact": "<contact information>",
    "description": "<detailed property description>",
    "images": [
        "<image url 1>",
        "<image url 2>",
        "..."
    ],
    "video": []
}

Base all details on the provided images and property information. Be specific and accurate in your descriptions.
"""
new_prompt= """
Analyze the provided images of the property and generate a compelling rental ad that highlights its unique features and appeals to potential renters.
It should be postable on online rental platforms like facebook marketplace, zillow, craigslist.

Key Points:

Property Description:
Provide a detailed description of the property's interior and exterior features.
Highlight the property's unique selling points, such as modern appliances, spacious rooms, or scenic views.
Use vivid language and imagery to create a compelling narrative.
Pricing and Availability:
Rent: Determine a competitive rent based on the property's location, size, and condition. Consider consulting local real estate market data.
Availability Date: Set the availability date to 10 days from the current date.
Security Deposit: Specify the required security deposit amount.

Additional Tips:
Use strong action verbs and positive language.
Highlight the property's proximity to amenities, transportation, and attractions.
Consider including a virtual tour or video walkthrough to provide a more immersive experience.
Use high-quality images that showcase the property's best features.
Proofread the ad carefully to ensure it is free of errors.

"""
# @weave.op
def generate(user_prompt):
    vertexai.init(project="vivid-argon-440517-e8", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        system_instruction=[textsi_1]
    )
    responses = model.generate_content(
        [image1, 
         image2, 
        # image3, image4, 
         user_prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    data = []
    for response in responses:
        data.append(response.text)
        print(response.text, end="")
    return data

def generate_v1():
    vertexai.init(project="vivid-argon-440517-e8", location="us-central1")
    variables = [
        {
            "media": [],
            "property_details": [],
        },
    ]
    prompt = Prompt(
        prompt_data=[text1],
        model_name="gemini-1.5-flash-002",
        variables=variables,
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    # Generate content using the assembled prompt. Change the index if you want
    # to use a different set in the variable value list.
    responses = prompt.generate_content(
        contents=prompt.assemble_contents(**prompt.variables[0]),
        stream=True,
    )

    for response in responses:
        print(response.text, end="")
 
# @weave.op
def multiturn_chat_agent():
    vertexai.init(project="vivid-argon-440517-e8", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        system_instruction=[system_prompt]
    )
    chat = model.start_chat()
    return chat

chat_agent = multiturn_chat_agent()
chat_generation_config = {
    "max_output_tokens": 1024,
    "stop_sequences": ["Ok", "Bye"],
    "temperature": 0.2,
    "response_mime_type": "application/json",
    "top_p": 0.95,
    }

def api_chat(user_input):
    response = chat_agent.send_message(
        [image1, 
        image2, user_input],
        generation_config=chat_generation_config,
        safety_settings=safety_settings
    )
    resp_dict = response.to_dict()
    system_answer = ""
    for data in resp_dict.get("candidates"):
        if "content" in data:
            content = data.get("content")
            for part in content.get("parts"):
                system_answer = ",".join([system_answer, part.get("text")])
    # print(system_answer)
    return system_answer
    
def chat():
    user_input = input("HI how can i help you")
    while True:
        response = chat_agent.send_message(
            [image1, 
         image2, user_input],
            generation_config=chat_generation_config,
            safety_settings=safety_settings
        )
        # print(response)
        # print(dir(response))
        # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_from_gapic', '_raw_response', 'candidates', 'from_dict', 'prompt_feedback', 'text', 'to_dict', 'usage_metadata']
        # print(response.to_dict())
        resp_dict = response.to_dict()
        for data in resp_dict.get("candidates"):
            if "content" in data:
                content = data.get("content")
                for part in content.get("parts"):
                    print(part.get("text"))
        user_input = input("...")
        if "Bye" in user_input:
            break
    
chat_thread = Thread(target=chat)
chat_thread.start()
           
image1 = Part.from_uri(
    mime_type="image/jpeg",
    uri="gs://reagent_data/902-904-Tacoma-12.jpg",
)
image2 = Part.from_uri(
    mime_type="image/jpeg",
    uri="gs://reagent_data/902-904-Tacoma-13.jpg",
)
# text1 = """Create a rental advertisement based on the photos {Rent}{Location}{Category}{External}{property_address}"""
textsi_1 = """You are Property Management Advisor.  Look through the media provided and create an online advertising . The Ad should be very attract for future tenants.  Add all the required details for a proper rent advertisement. This post will be reused in a online portal like facebook marketplace."""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.7,
    "top_p": 0.95,
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "OBJECT",
        "properties": {
            "response": {
                "type": "STRING",
                "description": "A JSON string containing the rental listing details"
            }
        }
    }
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

user_prompt = """Create a rental advertisement based on the photos {Rent}{Location}{Category}{External}{property_address}"""
# result, call = generate.call(user_prompt)

TVLY_KEY="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"



# Set up FastAPI app
app = FastAPI()
from pydantic import BaseModel
# Define Pydantic model for request body
class QueryModel(BaseModel):
    user_input: str
    
from typing import Optional
from pydantic import BaseModel, Field

class CorePropertyDetails(BaseModel):
    address: str
    square_feet: Optional[int] = 600
    bedrooms: Optional[int] = 2
    bathrooms: Optional[float] = 1.5
    monthly_rent: Optional[int] = 2000
    security_deposit: Optional[int] = 2000

class PropertyFeatures(BaseModel):
    pets_allowed: Optional[str] = "Allowed"
    laundry_type: Optional[str] = "In unit"
    air_conditioning: Optional[str] = "False"
    heating: Optional[str] = "Central"
    parking_type: Optional[str] = "Covered"
    shared_property: Optional[str] = "Yes"
    bathroom_type: Optional[str] = ""

class VisualsAndDescription(BaseModel):
    uploaded_files: list[str] = []
    description: str = ""

class AdditionalInformation(BaseModel):
    message: str = Field(None)  # Optional field

class Listing(BaseModel):
    core_details: CorePropertyDetails
    features: PropertyFeatures
    visuals_and_description: VisualsAndDescription
    additional_info: AdditionalInformation = Field(None)  # Optional field
    
# Define API endpoint
@app.post("/query/")
async def query_langchain(data: Listing):
    # user_input = data.user_input
    try:
        user_input = f"{data.additional_info.message} and Property Information: {data.model_dump_json()}"
        # Generate response using LangChain LLMChain
        response = api_chat(user_input=user_input)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
    