import streamlit as st
import replicate
import os

# app title
st.set_page_config(page_title="💬 mavericks bot")

# replicate credentials
with st.sidebar:
    st.title('💬 mavericks chatbot')
    st.write("This chatbot is built using Meta's open-source Llama 2 LLM for advanced language processing, combined with the Llava model to enhance its image recognition capabilities.")
    if 'replicate_api_token' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['replicate_api_token']
    else:
        replicate_api = st.text_input('Enter replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
            st.warning('Please enter your credentials!', icon='⚠')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['replicate_api_token'] = replicate_api

    st.subheader('Models and Parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['llama2-7b', 'llama2-13b'], key='selected_model')
    if selected_model == 'llama2-7b':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'llama2-13b':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('Top P', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('Max Length', min_value=32, max_value=4096, value=4096, step=32)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if the last message is not from the assistant
if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)

# Upload Image
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
