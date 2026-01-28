import streamlit as st
from openai import OpenAI
import PyPDF2

st.set_page_config(page_title="Lab 2")
# Show title and description.
st.title("MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets.OPEN_API_KEY
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    try:
        client = OpenAI(api_key=openai_api_key)
        client.models.list()
    except:
        st.error("API key not valid ")
        st.stop()

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader("Upload a document (.txt or .pdf)", type = ("txt", "pdf"))
    
    def read_pdf(uploaded_pdf):
        reader = PyPDF2.PdfReader(uploaded_pdf)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    
    question = option = st.radio(
    "Choose a Summary Option:",
    ["Summarize the document in 100 words", 
     "Summarize the document in 2 connecting paragraphs", 
     "Summarize the document in 5 bullet points"]
    )
    advanced = st.checkbox("Use advanced Model")
    
    if advanced:
        model = "gpt-4.1"
    else:
        model = "gpt-4.1-nano"
        
    button = st.button("Generate Response")
    if uploaded_file and question and button:

        if uploaded_file and question:
            file_extension = uploaded_file.name.split('.')[-1]
        if file_extension == 'txt':
            document = uploaded_file.read().decode()
        elif file_extension == 'pdf':
            document = read_pdf(uploaded_file)
        else:
            st.error("Unsupported file type.")

        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model= model,
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)