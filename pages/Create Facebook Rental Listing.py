"""Streamlit app for Rental Listing Assistant."""

# Import from standard library
import logging

# Import from 3rd party libraries
import streamlit as st
import streamlit_analytics
import requests
import json

# Import modules
import oai

# Import the Facebook marketplace posting function
from create_fb_marketplace_listing import post_facebook_marketplace_listing

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

# Configure Streamlit page
st.set_page_config(page_title="Rental Assistant", page_icon="🏠")

# Initialize session states
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your rental listing assistant. How can I help you create a listing today?"}
    ]

if "listed" not in st.session_state:
    st.session_state.listed = False

if "current_listing" not in st.session_state:
    st.session_state.current_listing = None

# Display title
st.title("Rental Listing Assistant")

# Show submission form if not yet submitted
if not st.session_state.submitted:
    with st.form("property_details"):
        st.write("Please provide your property details to begin")
        
        # Address input
        address = st.text_input("Property Address", placeholder="123 Market Street, San Francisco, CA")
        
        # Image upload
        uploaded_files = st.file_uploader(
            "Upload property images (you can select multiple files)", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True
        )

        # Submit button
        submit_button = st.form_submit_button("Start Chat")
        
        if submit_button:
            if not address:
                st.error("Please enter an address")
            elif not uploaded_files:
                st.error("Please upload at least one image")
            else:
                st.session_state.address = address
                st.session_state.images = uploaded_files
                
                # Make initial API call here
                api_url = "http://10.20.5.117:8000/query"
                
                # Prepare the initial payload
                payload = {
                    "core_details": {
                        "address": address,
                        # "square_feet": 0,
                        # "bedrooms": 0,
                        # "bathrooms": 2,
                        # "monthly_rent": 1200,
                        # "security_deposit": 2400
                    },
                    "features": {
                        # "pets_allowed": "string",
                        # "laundry_type": "string",
                        # "air_conditioning": "string",
                        # "heating": "string",
                        # "parking_type": "string",
                        # "shared_property": "string",
                        # "bathroom_type": "string"
                    },
                    "visuals_and_description": {
                        "uploaded_files": [
                            # Replace with actual image handling
                            "https://photos.zillowstatic.com/fp/0b9eceb0c092f9373978518faaf62aa5-cc_ft_1536.webp",
                            "https://photos.zillowstatic.com/fp/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.webp",
                            "https://photos.zillowstatic.com/fp/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.webp",
                            "https://photos.zillowstatic.com/fp/362e91b537ea78f33ae2bbab1561edb7-cc_ft_768.webp",
                            "https://photos.zillowstatic.com/fp/ccc608cdc87b07ffb26294fb10acff68-cc_ft_1536.webp",
                            "https://photos.zillowstatic.com/fp/1a9856a80e2dbaac9672cfb0b6efcbad-cc_ft_768.webp",
                            "https://photos.zillowstatic.com/fp/0278b53e7763004a2c8235006c90dd9c-cc_ft_768.webp"
                        ],
                        "description": "string"
                    },
                    "additional_info": {
                        "message": "Generate a rental listing for this property"
                    }
                }
                
                try:
                    with st.spinner("Generating initial listing..."):
                        response = requests.post(api_url, json=payload)
                        raw_response = json.loads(response.text)
                        
                        # Parse the nested JSON string and store in session state
                        st.session_state.current_listing = json.loads(raw_response['response'].lstrip(','))
                        
                        # Format the response with the new structure
                        initial_listing = f"""
                        📍 {st.session_state.current_listing.get('address', 'N/A')}
                        
                        🏠 {st.session_state.current_listing.get('bedrooms', 'N/A')} bed, {st.session_state.current_listing.get('bathrooms', 'N/A')} bath
                        💰 {st.session_state.current_listing.get('rent', 'N/A')}/month
                        
                        ✨ Amenities:
                        {', '.join(st.session_state.current_listing.get('amenities', ['None listed']))}
                        
                        📝 Description:
                        {st.session_state.current_listing.get('description', 'No description available')}
                        
                        """
                        
                        # Store the initial message in session state
                        st.session_state.messages = [
                            {"role": "assistant", "content": initial_listing}
                        ]
                        
                        st.session_state.submitted = True
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error generating listing: {str(e)}")
                    # Debug output
                    st.write("Raw response:", response.text)
                    st.stop()

# Show chat interface after submission
else:
    # Display uploaded images in a grid
    st.write("### Property Images")
    cols = st.columns(3)
    for idx, uploaded_file in enumerate(st.session_state.images):
        with cols[idx % 3]:
            st.image(uploaded_file, caption=f"Image {idx + 1}")
    
    st.write("### Property Address")
    st.info(st.session_state.address)
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add confirmation buttons after assistant messages if not listed
            if message["role"] == "assistant" and not st.session_state.listed:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm", 
                               key=f"confirm_{idx}", 
                               type="primary",
                               use_container_width=True):
                        try:
                            current_listing = st.session_state.current_listing
                            
                            # Get list of image paths from the images folder
                            image_paths = [
                                "./images/0b9eceb0c092f9373978518faaf62aa5-cc_ft_1536.jpg",
                                "./images/1a9856a80e2dbaac9672cfb0b6efcbad-cc_ft_768.jpg",
                                "./images/0278b53e7763004a2c8235006c90dd9c-cc_ft_768.jpg",
                                "./images/362e91b537ea78f33ae2bbab1561edb7-cc_ft_768.jpg",
                                "./images/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.jpg",
                                "./images/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.jpg",
                            ]
                            
                            # Convert the listing data to the format expected by Facebook marketplace
                            fb_property_details = {
                                "title": f"{current_listing.get('bedrooms')}B{current_listing.get('bathrooms')}B Rental Property",
                                "price": current_listing.get('rent', '').replace('$', '').replace('/month', ''),
                                "category": "Property Rentals",
                                "propertyType": "Apartment",
                                "rentalType": "Rent",
                                "privateRoom": True,
                                "bathroomType": "Private",
                                "bedrooms": str(current_listing.get('bedrooms', 1)),
                                "bathrooms": str(current_listing.get('bathrooms', 1)),
                                "address": current_listing.get('address', ''),
                                "description": current_listing.get('description', ''),
                                "location": current_listing.get('address', '').split(',')[-2].strip(),
                                "images": image_paths,  # Use the actual image paths
                                "numberOfResidents": "1"
                            }

                            # Facebook credentials
                            credentials = {
                                "username": "qiqimei1205@gmail.com",
                                "password": "Pux2oCsy1w"
                            }

                            # Post to Facebook Marketplace
                            post_facebook_marketplace_listing(credentials, fb_property_details)

                            st.session_state.listed = True
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": "Great! Your listing has been posted to Facebook Marketplace."
                            })
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error posting to Facebook Marketplace: {str(e)}")
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": f"Sorry, there was an error posting to Facebook Marketplace: {str(e)}"
                            })
                            st.rerun()

                with col2:
                    if st.button("Deny", 
                               key=f"deny_{idx}", 
                               type="secondary",
                               use_container_width=True):
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "I'll revise the listing. What would you like me to change?"
                        })
                        st.rerun()

    # Only show chat input if not listed
    if not st.session_state.listed:
        if prompt := st.chat_input("What would you like me to change about the listing?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Prepare the API request
                    api_url = "http://10.20.5.117:8000/query"
                    
                    # Prepare the structured payload with user feedback
                    payload = {
                        "core_details": {
                            "address": st.session_state.address,
                            # "square_feet": 0,  # These could be added to session state if known
                            # "bedrooms": 0,
                            # "bathrooms": 0,
                            # "monthly_rent": 1200,  # Could be from session state
                            # "security_deposit": 2400
                        },
                        "features": {
                            # "pets_allowed": "string",
                            # "laundry_type": "string",
                            # "air_conditioning": "string",
                            # "heating": "string",
                            # "parking_type": "string",
                            # "shared_property": "string",
                            # "bathroom_type": "string"
                        },
                        "visuals_and_description": {
                            "uploaded_files": [
                                # You'll need to implement proper image handling here
                                # This is just a placeholder
                                "https://photos.zillowstatic.com/fp/0b9eceb0c092f9373978518faaf62aa5-cc_ft_1536.webp",
                                "https://photos.zillowstatic.com/fp/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.webp",
                                "https://photos.zillowstatic.com/fp/39612dd9aafbadf0a17d9486138f0ef4-uncropped_scaled_within_1536_1152.webp",
                                "https://photos.zillowstatic.com/fp/362e91b537ea78f33ae2bbab1561edb7-cc_ft_768.webp",
                                "https://photos.zillowstatic.com/fp/ccc608cdc87b07ffb26294fb10acff68-cc_ft_1536.webp",
                                "https://photos.zillowstatic.com/fp/1a9856a80e2dbaac9672cfb0b6efcbad-cc_ft_768.webp",
                                "https://photos.zillowstatic.com/fp/0278b53e7763004a2c8235006c90dd9c-cc_ft_768.webp"
                            ],
                            "description": "string"
                        },
                        "additional_info": {
                            "message": f"Please update the listing with the following feedback: {prompt}"
                        }
                    }
                    
                    try:
                        response = requests.post(api_url, json=payload)
                        raw_response = json.loads(response.text)
                        
                        # Parse the nested JSON string
                        listing_json = json.loads(raw_response['response'].lstrip(','))
                        
                        # Format the updated listing
                        updated_listing = f"""
                        I've updated the listing based on your feedback. Here's the new version:

                        📍 {listing_json.get('address', 'N/A')}
                        
                        🏠 {listing_json.get('bedrooms', 'N/A')} bed, {listing_json.get('bathrooms', 'N/A')} bath
                        💰 {listing_json.get('rent', 'N/A')}/month
                        
                        ✨ Amenities:
                        {', '.join(listing_json.get('amenities', ['None listed']))}
                        

                        
                        📝 Description:
                        {listing_json.get('description', 'No description available')}
                        

                        
                        Is this more what you were looking for?
                        """
                        
                        # Add the message to session state and rerun to show buttons
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": updated_listing
                        })
                        st.rerun()  # This ensures the new message is displayed with buttons
                        
                    except Exception as e:
                        error_message = f"Error updating listing: {str(e)}"
                        st.error(error_message)
                        st.write("Raw response:", response.text)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_message
                        })

    if st.sidebar.button("Create New Listing"):
        st.session_state.clear()
        st.rerun()
