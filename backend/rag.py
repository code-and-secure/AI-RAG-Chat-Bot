import tempfile
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def process_file_bytes(file_bytes: bytes, filename: str):
    suffix = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        file_path = tmp.name

    if suffix == ".pdf":
        loader = PyPDFLoader(file_path)
    elif suffix == ".txt":
        loader = TextLoader(file_path)
    elif suffix == ".docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    documents = loader.load()
    os.unlink(file_path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    db = Chroma.from_documents(docs, get_embeddings())
    retriever = db.as_retriever(search_kwargs={"k": 3})
    return docs, db, retriever


def build_from_texts(texts: list[str], source_name: str):
    docs = [Document(page_content=t, metadata={"source": source_name}) for t in texts]
    db = Chroma.from_documents(docs, get_embeddings())
    retriever = db.as_retriever(search_kwargs={"k": 3})
    return docs, db, retriever


def build_from_scraped(scraped_text: str, url: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    temp_doc = Document(page_content=scraped_text, metadata={"source": url})
    docs = splitter.split_documents([temp_doc])
    db = Chroma.from_documents(docs, get_embeddings())
    retriever = db.as_retriever(search_kwargs={"k": 3})
    return docs, db, retriever
