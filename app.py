import streamlit as st
import os
import base64
from groq import Groq

# App title and configuration
st.set_page_config(page_title="💬 Mavericks Bot")

# Groq API Key
with st.sidebar:
    st.title('💬 Mavericks Chatbot')
    st.write("This chatbot uses the Groq LLaVA model for advanced language processing and image recognition.")

    if 'GROQ_API_KEY' in st.secrets:
        st.success('API key provided!', icon='✅')
        groq_api_key = st.secrets['GROQ_API_KEY']
    else:
        groq_api_key = st.text_input('Enter Groq API key:', type='password')
        if not groq_api_key:
            st.warning('Please enter valid Groq API credentials!', icon='⚠')

    os.environ['GROQ_API_KEY'] = groq_api_key

# Store LLaVA generated responses
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Model parameters
temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
top_p = st.sidebar.slider('Top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
max_length = st.sidebar.slider('Max Length', min_value=32, max_value=4096, value=4096, step=32)

# Function to encode and process image with Groq LLaVA
def process_image_and_text(image=None, text=None):
    client = Groq(api_key=groq_api_key)
    
    # Append the Maverick Bot prompt to the user message
    maverick_prompt = ("You are Maverick Bot, an advanced AI assistant created by Team Mavericks. "
                       "You possess sophisticated image recognition capabilities, allowing you to analyze and understand visual content. "
                       "When interacting with users, you should leverage these capabilities to provide accurate and insightful responses related to the images they provide. "
                       "Your primary function is to assist users by interpreting images and integrating this information into your responses.\n")
    
    full_prompt = maverick_prompt + (text if text else "")
    
    messages = [{"type": "text", "text": full_prompt}]
    
    if image:
        base64_image = base64.b64encode(image.read()).decode('utf-8')
        messages.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": messages}],
        model="llava-v1.5-7b-4096-preview",
        temperature=temperature,
        top_p=top_p,
        max_length=max_length
    )

    return chat_completion.choices[0].message.content

# User input: Text and/or Image
image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
prompt = st.chat_input(placeholder="Type your message here...")

# Display uploaded image and process input
if prompt or image:
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    if image:
        st.image(image, caption="Uploaded Image", use_column_width=True)  # Display the uploaded image

    # Generate LLaVA response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response = process_image_and_text(image=image, text=prompt)
            placeholder = st.empty()
            placeholder.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
