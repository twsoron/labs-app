import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str

if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None

st.title("Lab 6")
st.write("Ask a question below.")
st.caption("Web search is enabled for up-to-date answers.")

structured_summary = st.sidebar.checkbox("Return structured summary")
use_streaming = st.sidebar.checkbox("Use streaming")
client = OpenAI(api_key=st.secrets.OPEN_API_KEY)

question = st.text_input("Enter your question:")
if question:
    if structured_summary:
        response = client.responses.parse(
            model = "gpt-4o",
            input = question,
            instructions = "Extract the answer into the structured format.",
            tools = [{"type": "web_search_preview"}],
            text_format = ResearchSummary
        )

        summary = response.output_parsed
        st.write("Response:")
        st.write(summary.main_answer)
        st.write("Key Facts:")
        for fact in summary.key_facts:
            st.write("- " + fact)
        st.caption(summary.source_hint)

        st.session_state.last_response_id = response.id

    else:
        if use_streaming:
            st.write("Response:")
            placeholder = st.empty()
            full_text = ""

            with client.responses.stream(
                model = "gpt-4o",
                instructions = "You are a helpful research assistant. Cite your sources.",
                input = question,
                tools = [{"type": "web_search_preview"}]
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        full_text += event.delta
                        placeholder.write(full_text)

                final_response = stream.get_final_response()

            st.session_state.last_response_id = final_response.id

        else:
            response = client.responses.create(
                model = "gpt-4o",
                instructions = "You are a helpful research assistant. Cite your sources.",
                input = question,
                tools = [{"type": "web_search_preview"}]
            )

            st.write("Response:")
            st.write(response.output_text)

            st.session_state.last_response_id = response.id

if st.session_state.last_response_id is not None:
    follow_up = st.text_input("Ask a follow-up question:")

    if follow_up:
        if structured_summary:
            follow_up_response = client.responses.parse(
                model = "gpt-4o",
                input = follow_up,
                instructions = "Extract the answer into the structured format.",
                tools = [{"type": "web_search_preview"}],
                text_format = ResearchSummary
            )
            summary = follow_up_response.output_parsed

            st.write("Follow-up Response:")
            st.write(summary.main_answer)
            st.write("Key Facts:")
            for fact in summary.key_facts:
                st.write("- " + fact)
            st.caption(summary.source_hint)

        else:
            if use_streaming:
                st.write("Follow-up Response:")
                placeholder = st.empty()
                full_text = ""

                with client.responses.stream(
                    model = "gpt-4o",
                    input = follow_up,
                    instructions = "You are a helpful research assistant. Cite your sources.",
                    tools = [{"type": "web_search_preview"}],
                    previous_response_id = st.session_state.last_response_id
                ) as stream:
                    for event in stream:
                        if event.type == "response.output_text.delta":
                            full_text += event.delta
                            placeholder.write(full_text)

                    final_response = stream.get_final_response()

            else:
                follow_up_response = client.responses.create(
                    model = "gpt-4o",
                    input = follow_up,
                    instructions = "You are a helpful research assistant. Cite your sources.",
                    tools = [{"type": "web_search_preview"}],
                    previous_response_id = st.session_state.last_response_id
                )
                st.write(follow_up_response.output_text)
