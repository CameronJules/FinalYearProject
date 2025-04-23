import streamlit as st
import boto3
from io import BytesIO
import requests
from base64 import b64decode
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get('API_KEY')

url = "https://5vawmc8ccc.execute-api.eu-west-1.amazonaws.com/dev/audio-genre"
headers = {
'isBase64Encoded': 'true',
'Content-Type': 'audio/mpeg',
'x-api-key': api_key
}


def generate_page(url, headers):
    st.set_page_config(page_title="Pitch Shift Demo")

    st.title("Genre Detection Demo")

    st.text(
        '''
            Genre detection serves as basis for running ML functionality on audio in the cloud.
            This shows that non-standard audio functions can be run and any further optimised
            models can be created and distributed for use via serverless APIs.
        '''
    )



    # File upload
    with st.container(border=True):
        uploaded_file = st.file_uploader(label="Upload MP3 file here", type="mp3")
        top_n = st.number_input("Insert number of genres to return (Top n genres)",step=1)
        if top_n > 0:
            url = url+f"?top_n={top_n}"
        
        if uploaded_file is not None:
            st.subheader("Sample Player")
            test_bytes_data = uploaded_file.getvalue()
            playable_bytes = BytesIO(test_bytes_data)
            st.audio(playable_bytes, format='audio/mpeg')
        

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

            st.subheader("URL String")
            st.info(url)



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



generate_page(url, headers)






