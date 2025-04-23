import streamlit as st
import requests
from base64 import b64decode, b64encode
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get('API_KEY')

url = "https://5vawmc8ccc.execute-api.eu-west-1.amazonaws.com/dev/average-audio-energy"
headers = {
'isBase64Encoded': 'true',
'Content-Type': 'audio/mpeg',
'x-api-key': api_key
}


def generate_page():
    st.set_page_config(page_title="Audio Energy Demo")

    st.title("Audio Energy Demo")

    st.text(
        '''
        This page uses the API gateway endpoint for calculating audio energy. \n
        It provides an example of a basic audio function running via the API, in this case
        average audio energy provides a quantitative measure of loudness or intensity of
        audio. Many other functions that provide simple analysis can also be included via a 
        similar method of implementation. In this case the output is non audio
        '''
    )



    # File upload
    with st.container(height=200):
        uploaded_file = st.file_uploader(label="Upload MP3 file here", type="mp3")

    # Genereate rest of the page once file is uploaded
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue() # Get bytes value
        

        # Display for input to API gateway
        with st.expander("Input Payload"):
            st.subheader("Headers")
            example_headers = {
                'isBase64Encoded': 'true',
                'Content-Type': 'audio/mpeg',
                'x-api-key': 'api-key goes here'
                }
            st.json(example_headers)

            st.subheader("Payload")
            st.text("Directly use the raw binary data and let api gateway handle it")


        run = st.button("Call API", use_container_width=True, type='primary')

        if run:
            # Run using post and raw data payload
            response = requests.request("POST", url, headers=headers, data=bytes_data)

            with st.container(height=200):
                if response.status_code == 200:
                    st.success(f"Status Code: {response.status_code}")
                else:
                    st.warning(f"Status Code: {response.status_code}")
                st.info(f"Response Body: {response.text}")



generate_page()






