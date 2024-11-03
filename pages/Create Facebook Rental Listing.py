"""Streamlit app for Rental Listing Assistant."""

# Import from standard library
import logging

# Import from 3rd party libraries
import streamlit as st
import streamlit_analytics

# Import modules
import oai

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
                st.session_state.submitted = True
                st.rerun()  # Rerun the app to show the chat interface

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
                        st.session_state.listed = True
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "Great! Your listing has been confirmed and will be posted to Facebook Marketplace."
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
        if prompt := st.chat_input("What would you like help with?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = "I'm on it!"
                    st.markdown(response)
                    
            st.session_state.messages.append({"role": "assistant", "content": response})

    if st.sidebar.button("Create New Listing"):
        st.session_state.clear()
        st.rerun()
