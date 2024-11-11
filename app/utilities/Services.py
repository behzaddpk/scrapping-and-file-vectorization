import os
import json
import openai
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import PyPDF2
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.database import get_db
from app.models.Data_model import Data

# Set your OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class EmbeddingService:
    def __init__(self, model_name="text-embedding-3-small"):
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=model_name)

    def get_embeddings(self, text: str):
        if isinstance(text, list):
            text = ' '.join(text)
        return self.embeddings.embed_documents([text])[0]

class VectorizationService:
    def __init__(self, model_name="text-embedding-3-small"):
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    @staticmethod
    def load_documents(path: str, extension: str, metadata: dict):
        if extension == '.pdf':
            text = ''
            with open(path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text()
            document = [Document(page_content=text, metadata=metadata)]
        elif extension == ".txt":
            document = TextLoader(path).load()
        else:
            raise ValueError("Unsupported file format")
        return document


    def vector_document(self, documents):
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        document_chunks = text_splitter.split_documents(documents)
        vectors = [self.embeddings.embed_documents([chunk.page_content])[0] for chunk in document_chunks]
        return vectors, [chunk.page_content for chunk in document_chunks]

    def search_similar(self, prompt: str, db: Session):
        if isinstance(prompt, list):
            prompt = ' '.join(prompt)

        embedding = self.embeddings.embed_documents([prompt])[0]

        data_records = db.query(Data).all()
        documents = [Document(page_content=record.content, metadata={"file_name": record.resource}) for record in data_records]

        if len(documents) == 0:
            return []

        try:
            vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings(api_key=OPENAI_API_KEY, model='text-embedding-3-small'))
            results = vectorstore.similarity_search(prompt, k=1)
            return results
        except Exception as e:
            return []

