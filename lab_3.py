import streamlit as st
from openai import OpenAI

system_msg = [{'role': 'system', 'content': 'Explain the response so a 10 year old can understand, keep answers to a medium length.'}]
if 'client' not in st.session_state:
    openai_api_key = st.secrets.OPEN_API_KEY
    st.session_state.client = OpenAI(api_key=openai_api_key)

if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role': 'assistant', 'content': 'How can I help you?'}]

for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

if prompt := st.chat_input("What is up?"):

    if prompt.lower().strip() == "no":
        st.session_state.messages = [
            {"role": "assistant", "content": "Anything else I can help with?"}]
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    client = st.session_state.client
    stream = client.chat.completions.create(
        model= 'gpt-4.1',
        messages= system_msg + st.session_state.messages,
        stream=True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    
    followup = "Would you like more info? (yes/no)"
    with st.chat_message("assistant"):
        st.markdown(followup)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": followup})
    st.session_state.messages = st.session_state.messages[-6:]
