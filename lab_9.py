import streamlit as st
import json
import os
from openai import OpenAI

st.title("Chatbot with Long-Term Memory")

if "openai_client" not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets.OPEN_API_KEY)

def load_memories():
    if os.path.exists("memories.json"):
        with open("memories.json", "r") as f:
            return json.load(f)
    return []

def save_memories(memories):
    with open("memories.json", "w") as f:
        json.dump(memories, f)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "memories" not in st.session_state:
    st.session_state.memories = load_memories()

st.sidebar.title("Memories")
memories = load_memories()

if memories:
    for m in memories:
        st.sidebar.write(f"- {m}")
else:
    st.sidebar.write("No memories yet. Start chatting!")

if st.sidebar.button("Clear All Memories"):
    save_memories([])
    st.session_state.memories = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Say something")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    memories = load_memories()

    system_message = "You are a helpful assistant."
    if memories:
        memory_str = "\n".join([f"- {m}" for m in memories])
        system_message += (
            "\n\nHere are things you remember about this user "
            "from past conversations:\n" + memory_str +
            "\nUse this information to personalize your responses."
        )

    messages = [{"role": "system", "content": system_message}]
    messages += st.session_state.messages

    response = st.session_state.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    with st.chat_message("assistant"):
        st.write(assistant_reply)

    user_msg = st.session_state.messages[-2]["content"]
    assistant_msg = st.session_state.messages[-1]["content"]

    extraction_prompt = f"""Analyze this conversation and extract new facts
about the user worth remembering (name, preferences, location, interests, etc.)

Already known memories:
{json.dumps(memories)}

User message: {user_msg}
Assistant response: {assistant_msg}

Return ONLY a JSON list of new facts. If no new facts, return [].
Example: ["User's name is Ava", "User studies at Syracuse University"]"""

    response = st.session_state.openai_client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    try:
        new_memories = json.loads(response.choices[0].message.content)
        if new_memories:
            memories.extend(new_memories)
            memories = list(dict.fromkeys(memories))
            save_memories(memories)
            st.session_state.memories = memories
    except json.JSONDecodeError:
        pass