import streamlit as st
import requests
from base64 import b64decode
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get('API_KEY')

url = "https://5vawmc8ccc.execute-api.eu-west-1.amazonaws.com/dev/audio-pitch-shift"
headers = {
'isBase64Encoded': 'true',
'Content-Type': 'audio/mpeg',
'x-api-key': api_key
}


def generate_page(url, headers):
    st.set_page_config(page_title="Pitch Shift Demo")

    st.title("Pitch Shift Demo")

    st.text(
        '''
            This is a demo for pitch shifting an audio file, this serves as a basis
            for general audio manipulation techniques through cloud APIs. This uses
            a hand written implementation over the use of heavy weight libraries
            this give direct and light weight access of audio functions to 
            developers without any deep understanding of the audio space. The general
            functionality was created in under 30 minutes which is significantly less time
            than development of the function.
            
            This demo also serves as basis for returning audio files from the API.
        '''
    )



    # File upload
    with st.container(border=True):
        uploaded_file = st.file_uploader(label="Upload MP3 file here", type="mp3")
        shift_amount = st.number_input("Insert Shift Amount (Number of semitones to shift up or down)",step=1)
        if shift_amount != 0:
            url = url+f"?shift_amount={shift_amount}"
        
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

                if response.status_code == 200:
                    # Convert response back to audio
                    binary_data = b64decode(response.text)
                    byte_data = BytesIO(binary_data)
                    st.subheader("Response Audio")
                    st.audio(byte_data, format='audio/mpeg')

                else:
                    st.info(f"Response Body: {response.text}")



generate_page(url, headers)






