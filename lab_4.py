import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from openai import OpenAI
import chromadb
from pathlib import Path
from PyPDF2 import PdfReader



chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_Lab')
collection = chroma_client.get_or_create_collection('Lab4Collection')

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets.OPEN_API_KEY)

def add_to_collection(collection, text, file_name):
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )
    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids=file_name,
        embeddings=[embedding]
    )


def extract_text_from_pdf(pdf_path):
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text


def load_pdfs_to_collection(folder_path: str, collection) -> int:
    folder = Path(folder_path)
    pdf_paths = sorted(folder.glob("*.pdf"))

    loaded = 0
    for pdf_path in pdf_paths:
        text = extract_text_from_pdf(str(pdf_path))
        file_id = pdf_path.name

        try:
            collection.add(
                documents=[text],
                ids=[file_id]
            )
            loaded += 1
        except Exception:
            pass

    return loaded


if collection.count() == 0:
    loaded = load_pdfs_to_collection("./Lab-04-Data/", collection)


st.title('Lab 4: Chatbot using RAG')

topic = st.sidebar.text_input(
    'Topic',
    placeholder='Type your topic (e.g., GenAI)...'
)

if topic:
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=topic,
        model='text-embedding-3-small'
    )

    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    st.subheader(f'Results for: {topic}')

    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        st.write(f'**{i+1}. {doc_id}**')
else:
    st.info('Enter a topic in the sidebar to search the collection')