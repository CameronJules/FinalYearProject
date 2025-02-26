import base64
import json

# Read the binary MPEG file and encode it to Base64
with open("../music_files/9353__guitarz1970__tinsing-1 copy.mp3", "rb") as audio_file:
    encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")

# Create the JSON payload
payload = {
    "headers": {
        "Content-Type": "audio/mpeg"
    },
    "body": encoded_audio,  # Base64-encoded binary data
    "isBase64Encoded": True  # AWS Lambda-specific flag
}

# Save to a JSON file
with open("./test_payload.json", "w") as json_file:
    json.dump(payload, json_file, indent=4)

print("Base64-encoded JSON payload saved as test_payload.json")
