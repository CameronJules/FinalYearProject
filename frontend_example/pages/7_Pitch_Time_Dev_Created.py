import streamlit as st
import requests
from base64 import b64decode
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get('API_KEY')

pitch_url_base = "https://5vawmc8ccc.execute-api.eu-west-1.amazonaws.com/dev/audio-pitch-shift"
time_url_base = "https://5vawmc8ccc.execute-api.eu-west-1.amazonaws.com/dev/time-stretch"
headers = {
    'isBase64Encoded': 'true',
    'Content-Type': 'audio/mpeg',
    'x-api-key': api_key
}


def generate_page(pitch_url_base, time_url_base, headers):
    st.set_page_config(page_title="Pitch Shift Demo")
    st.title("Pitch Time Chain Developer Implementation Demo")

    st.text(
        '''
        This shows function chaining if implemented directly by developers using the API
        rather than the API provider (me)
        '''
    )

    with st.container(border=True):
        uploaded_file = st.file_uploader(label="Upload MP3 file here", type="mp3")
        shift_amount = st.number_input("Insert Shift Amount (Number of semitones to shift up or down)", step=1)
        stretch_amount = st.number_input("Insert Stretch Amount (Multiplier on duration e.g 1.5x makes it 1.5 times faster)", step=0.25)

        if uploaded_file is not None:
            st.subheader("Sample Player")
            test_bytes_data = uploaded_file.getvalue()
            playable_bytes = BytesIO(test_bytes_data)
            st.audio(playable_bytes, format='audio/mpeg')

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        pitch_url = pitch_url_base
        if shift_amount != 0:
            pitch_url += f"?shift_amount={shift_amount}"

        time_url = time_url_base
        if stretch_amount != 0:
            time_url += f"?stretch_amount={stretch_amount}"

        with st.expander("Input Payload"):
            st.subheader("Headers")
            st.json({
                'isBase64Encoded': 'true',
                'Content-Type': 'audio/mpeg',
                'x-api-key': 'api-key goes here'
            })

            st.subheader("Payload")
            st.text("Directly use the raw binary data and let API Gateway handle it")

            st.subheader("URL String")
            st.info(pitch_url)
            st.info(time_url)

        run = st.button("Call API", use_container_width=True, type='primary')

        if run:
            response = requests.post(pitch_url, headers=headers, data=bytes_data)

            with st.container(height=200):
                if response.status_code == 200:
                    st.success(f"Pitch API Status Code: {response.status_code}")
                    binary_data = b64decode(response.text)
                    pitch_output = BytesIO(binary_data)

                    st.subheader("Pitch Response Audio")
                    st.audio(pitch_output, format='audio/mpeg')

                    # Pass to Time Stretch
                    time_response = requests.post(time_url, headers=headers, data=pitch_output.getvalue())
                    if time_response.status_code == 200:
                        time_binary_data = b64decode(time_response.text)
                        time_output = BytesIO(time_binary_data)

                        st.subheader("Time Response Audio (After Pitch)")
                        st.audio(time_output, format='audio/mpeg')
                    else:
                        st.error(f"Time Stretch API Failed: {time_response.status_code}")
                        st.text(time_response.text)
                else:
                    st.warning(f"Pitch API Failed: {response.status_code}")
                    st.text(response.text)


generate_page(pitch_url_base, time_url_base, headers)
