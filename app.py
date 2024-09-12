from groq import groq
import base64
import streamlit as st
import os

# Function to encode the image with size check
def encode_image(image_file):
    # Check if the file size is within the limit (4 MB = 4 * 1024 * 1024 bytes)
    if image_file.size > 4 * 1024 * 1024:
        st.error("File size exceeds 4 MB. Please upload a smaller image.")
        return None

    return base64.b64encode(image_file.read()).decode('utf-8')

# Streamlit app
st.title("Image Upload for LLM API")

# Upload image
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_image is not None:
    # Getting the base64 string
    base64_image = encode_image(uploaded_image)

    if base64_image is not None:  # Ensure base64_image is valid
        client = groq()

        # Prepare the API request
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "what's in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llava-v1.5-7b-4096-preview",
        )

        # Display the result
        st.success("API Response:")
        st.write(chat_completion.choices[0].message.content)
