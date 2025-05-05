import streamlit as st
import requests
from base64 import b64decode, b64encode
from io import BytesIO
import json



url = "https://5vawmc8ccc.execute-api.eu-west-1.amazonaws.com/dev/pitch-time-chain"
headers = {
    'Content-Type':'application/json',
    'x-api-key': '3borWufDVg8UWfjFLBV3E6iZ8UQpvehzecMkAY06'
}


def generate_page(url, headers):
    st.set_page_config(page_title="Pitch and Time Chaining Demo")

    st.title("Pitch and Time Chaining Demo")

    st.text(
        '''
            The goal of this endpoint was to chain functions together using AWS step functions.
            This allows various elements to be run in a specified order.

            I have found an issue with using step functions which has been documented. The main
            problem is that step functions use json for each states input. This means there is
            a limit on how long / large the json can be. As a result, any encoded audio longer than 5s
            breaches this limit and prevents the payload from being sent.
            
            This functionality - chaining endpoints - can be easily replicated by app developers by simply
            calling each function sequentially in implementation. From service provider standpoint this reduces
            the cloud overhead to run a chained service because step functions cost more to run.
        '''
    )



    # File upload
    with st.container(border=True):
        uploaded_file = st.file_uploader(label="Upload MP3 file here", type="mp3")
        shift_amount = st.number_input("Insert Shift Amount (Number of semitones to shift up or down)",step=1)

        stretch_amount = st.number_input("Insert Stretch Amount (Multiplier on duration e.g 1.5x makes it 1.5 times faster)",step=0.25)
        
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
                'Content-Type': 'application/json',
                'x-api-key': 'api-key goes here'
                }
            st.json(example_headers)

            st.subheader("Payload")
            st.text("Step functions underneath now require the payload directly as json, In this case we need to build up the payload")
            payload = json.dumps({
                "queryStringParameters": {
                    "shift_amount": shift_amount,
                    "stretch_amount": stretch_amount
                },
                "body" : b64encode(bytes_data).decode("utf-8"),
                "isBase64Encoded" : True
            })

            st.json(payload)

            st.subheader("URL String")
            st.info(url)



        run = st.button("Call API", use_container_width=True, type='primary')

        if run:
            # Run using post and raw data payload
            response = requests.request("POST", url, headers=headers, data=payload)

            with st.container(height=400):
                if response.status_code == 200:
                    st.success(f"Status Code: {response.status_code}")
                else:
                    st.warning(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    response = json.loads(response.text)
                    st.json(response)
                    binary_data = b64decode(response["body"])
                    byte_data = BytesIO(binary_data)
                    st.subheader("Response Audio")
                    st.audio(byte_data, format='audio/mpeg')




generate_page(url, headers)






