import streamlit as st
import replicate
import os
import base64
from groq import Groq

# App title and configuration
st.set_page_config(page_title="💬 Mavericks Bot")

# Replicate and Groq Credentials
with st.sidebar:
    st.title('💬 Mavericks Chatbot')
    st.write("This chatbot is built using Meta's open-source Llama 2 LLM for advanced language processing, combined with the Llava model to enhance its image recognition capabilities.")
    
    if 'REPLICATE_API_TOKEN' in st.secrets and 'GROQ_API_KEY' in st.secrets:
        st.success('API keys provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
        groq_api_key = st.secrets['GROQ_API_KEY']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        groq_api_key = st.text_input('Enter Groq API key:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
            st.warning('Please enter valid Replicate API credentials!', icon='⚠')
        if not (groq_api_key):
            st.warning('Please enter valid Groq API credentials!', icon='⚠')
    
    os.environ['REPLICATE_API_TOKEN'] = replicate_api
    os.environ['GROQ_API_KEY'] = groq_api_key

    st.subheader('Models and parameters')
    selected_model = st.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'])
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    else:
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'

    temperature = st.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.slider('max_length', min_value=32, max_value=4096, value=4096, step=32)

# Store LLM generated responses
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    string_dialogue = "You are Mavericks Bot, an advanced AI assistant created by Team Mavericks. You possess sophisticated image recognition capabilities, allowing you to analyze and understand visual content."
    for dict_message in st.session_state.messages:
        string_dialogue += f"{dict_message['role'].capitalize()}: {dict_message['content']}\n\n"
    
    output = replicate.run(llm, input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                       "temperature": temperature, "top_p": top_p, "max_length": max_length, "repetition_penalty": 1})
    return output

# Function to encode and process image with Groq LLaVA
def process_image(image):
    base64_image = base64.b64encode(image.read()).decode('utf-8')
    client = Groq(api_key=groq_api_key)
    
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the image. Note: your response will be again passed to another llm."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ],
        }],
        model="llava-v1.5-7b-4096-preview",
    )
    
    return chat_completion.choices[0].message.content

# User input
image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
prompt = st.chat_input(disabled=not replicate_api or not groq_api_key)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Process image if uploaded
    if image:
        with st.spinner("Processing image..."):
            image_description = process_image(image)
            st.session_state.messages.append({"role": "assistant", "content": image_description})
            prompt += f" (Image description: {image_description})"
    
    # Generate Llama2 response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''.join(response)
            placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
