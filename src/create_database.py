from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

import openai
from openai import RateLimitError
from dotenv import load_dotenv
import os
import shutil
import time

load_dotenv(dotenv_path="key.env")

openai.api_key = os.getenv('OPENAI_API_KEY')

if openai.api_key is None:
    raise ValueError("OpenAI API key not found. Please check your .env file.")

CHROMA_PATH = "chroma"
DATA_PATH = "D:\Coding\RAG Based Chatbot\Data"

def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 300,
        chunk_overlap = 100,
        length_function = len,
        add_start_index = True,
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma(
        embedding_function=OpenAIEmbeddings(), persist_directory = CHROMA_PATH
    )

    for chunk in chunks:
        try:
            db.add_documents([chunk])
        except RateLimitError:
            print("Rate Limit Exceeded. Waiting for 60 seconds.....")
            time.sleep(60)
            db.add_documents([chunk])

    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}")

if __name__ == "__main__":
    main()
