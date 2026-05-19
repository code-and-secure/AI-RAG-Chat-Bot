import tempfile
import os
import streamlit as st
import streamlit.components.v1 as components
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from googlesearch import search
from duckduckgo_search import DDGS

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_groq import ChatGroq

# =========================
# LOAD ENV
# =========================
load_dotenv()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI RAG Assistant",
    page_icon="�",
    layout="wide"
)

# =========================
# LOAD CSS
# =========================
def load_css():
    with open("style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()


def fetch_page_text(url: str, max_chars: int = 4000) -> str:
    """Fetch and clean visible text from a webpage for LLM context."""
    try:
        response = requests.get(
            url,
            timeout=8,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = " ".join(soup.get_text(separator=" ").split())
        return text[:max_chars]
    except Exception:
        return ""


def google_search_context(user_query: str, num_results: int = 3):
    """Return concatenated web context and source URLs from Google results."""
    urls = []
    context_parts = []

    try:
        for url in search(user_query, num_results=num_results):
            urls.append(url)
            page_text = fetch_page_text(url)
            if page_text:
                context_parts.append(f"Source: {url}\nContent: {page_text}")
    except Exception:
        pass

    # Fallback provider when Google blocks automated requests.
    if not context_parts:
        try:
            with DDGS() as ddgs:
                results = ddgs.text(user_query, max_results=num_results)
                for item in results:
                    url = item.get("href")
                    if not url:
                        continue
                    urls.append(url)
                    page_text = fetch_page_text(url)
                    if page_text:
                        context_parts.append(f"Source: {url}\nContent: {page_text}")
        except Exception:
            return "", []

    return "\n\n".join(context_parts), urls

# =========================
# INITIALIZE SESSION STATE
# =========================
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "docs" not in st.session_state:
    st.session_state.docs = []
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "submitted_query" not in st.session_state:
    st.session_state.submitted_query = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# LOAD HERO HTML
# =========================
with open("hero.html", "r") as f:
    hero_html = f.read()

with open("style.css", "r") as f:
    css = f.read()

components.html(
    f"""
    <html>
    <head>
        <style>
        {css}
        </style>
    </head>

    <body>

    {hero_html}

    </body>
    </html>
    """,
    height=450,
    scrolling=False
)

# =========================
# FILE UPLOADER - ONLY SHOW IF NO FILE UPLOADED
# =========================
if not st.session_state.file_uploaded:
    uploaded_files = st.file_uploader(
        "� Upload PDF, TXT, DOCX",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )

    # =========================
    # PROCESS DOCUMENT
    # =========================
    if uploaded_files:
        if len(uploaded_files) > 1:
            st.warning(
                "Only single documents are supported right now. Multiple documents will be supported in the future."
            )
            st.stop()

        uploaded_file = uploaded_files[0]

        with st.spinner("� Processing document..."):

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
                tmp_file.write(uploaded_file.read())
                file_path = tmp_file.name

            # =========================
            # DOCUMENT LOADER
            # =========================
            if uploaded_file.name.endswith(".pdf"):
                loader = PyPDFLoader(file_path)

            elif uploaded_file.name.endswith(".txt"):
                loader = TextLoader(file_path)

            elif uploaded_file.name.endswith(".docx"):
                loader = Docx2txtLoader(file_path)

            else:
                st.error("Unsupported file type")
                st.stop()

            # Load document
            documents = loader.load()

            # =========================
            # TEXT SPLITTING
            # =========================
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=700,
                chunk_overlap=100
            )

            docs = splitter.split_documents(documents)

            # Store in session state
            st.session_state.docs = docs
            st.session_state.file_uploaded = True
            st.session_state.uploaded_file_name = uploaded_file.name

            # =========================
            # FREE EMBEDDINGS
            # =========================
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

            # =========================
            # VECTOR DATABASE
            # =========================
            db = Chroma.from_documents(
                docs,
                embeddings
            )

            # =========================
            # RETRIEVER
            # =========================
            st.session_state.retriever = db.as_retriever(
                search_kwargs={"k": 3}
            )
            st.session_state.vector_db = db

            # Clear previous queries
            st.session_state.submitted_query = ""
            st.session_state.last_response = ""
            st.session_state.chat_history = []

            # Rerun to hide upload box
            st.rerun()

else:
    # =========================
    # FILE INFO - CLEAN NO BOX
    # =========================
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 0;
                margin-bottom: 20px;
            ">
                <span style="font-size: 16px;">�</span>
                <span style="color: white; font-size: 14px; font-weight: 500;">{st.session_state.uploaded_file_name}</span>
                <span style="color: #d8b4fe; font-size: 13px;">• {len(st.session_state.docs)} chunks</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        if st.button("� Upload New", use_container_width=True, key="upload_new_btn"):
            st.session_state.file_uploaded = False
            st.session_state.docs = []
            st.session_state.retriever = None
            st.session_state.vector_db = None
            st.session_state.uploaded_file_name = None
            st.session_state.submitted_query = ""
            st.session_state.last_response = ""
            st.session_state.chat_history = []
            st.rerun()

    # =========================
    # CHAT CONTAINER
    # =========================
    st.markdown(
        '<div class="chat-container">',
        unsafe_allow_html=True
    )

    # =========================
    # QUESTION INPUT - FORM FOR ENTER KEY SUPPORT
    # =========================
    with st.form(key="search_form", clear_on_submit=False):
        st.markdown(
            '<p class="input-label">� Ask anything from your document</p>',
            unsafe_allow_html=True
        )

        query_col1, query_col2 = st.columns([5, 1])

        with query_col1:
            query = st.text_input(
                "Question",
                key="query_input",
                placeholder="Type your question here...",
                label_visibility="collapsed"
            )

        with query_col2:
            search_clicked = st.form_submit_button(
                "� Search",
                use_container_width=True
            )

    # =========================
    # PROCESS QUERY
    # =========================
    if query and search_clicked:
        st.session_state.submitted_query = query

        with st.spinner("� AI is thinking..."):

            # Normalize user query for more consistent retrieval behavior.
            normalized_query = query.strip().lower()

            # Retrieve chunks with relevance scores when possible.
            scored_docs = []
            if st.session_state.vector_db is not None:
                try:
                    scored_docs = st.session_state.vector_db.similarity_search_with_relevance_scores(
                        normalized_query,
                        k=4,
                    )
                except Exception:
                    scored_docs = []

            best_score = 0.0
            if scored_docs:
                best_score = scored_docs[0][1]
                # Keep top chunks even with moderate scores to avoid false negatives.
                relevant_docs = [doc for doc, _ in scored_docs[:5]]
            else:
                relevant_docs = st.session_state.retriever.invoke(normalized_query)

            # Combine retrieved context
            context = "\n\n".join(
                [doc.page_content for doc in relevant_docs]
            )

            # Prompt
            prompt = f"""
            You are a helpful AI assistant for document Q&A.

            Rules:
            1) Answer using only the context below.
            2) If the context partially answers, give the best direct answer and clearly say what is missing.
            3) Do NOT include internal reasoning, meta commentary, or phrases like
               "let me think", "based on the context", or "the user asked".
            4) Keep the answer clean, final, and user-facing.
            5) If context does not contain the answer at all, reply exactly:
               "I could not find this in the uploaded document."

            Context:
            {context}

            Question:
            {query}
            """

            no_data_message = (
                "Data is not available in the uploaded documents. "
                "Now searching from Google."
            )

            # AI response
            if not os.getenv("GROQ_API_KEY"):
                st.error("GROQ_API_KEY is missing. Add it to your .env file.")
                st.stop()

            llm = ChatGroq(
                model="qwen/qwen3-32b",
                temperature=0.3
            )

            # Fallback only when retrieval confidence is very low.
            should_fallback_to_web = len(relevant_docs) == 0 or best_score < 0.08
            final_answer = ""

            if not should_fallback_to_web:
                response = llm.invoke(prompt)
                final_answer = response.content
                if "I could not find this in the uploaded document." in response.content and best_score < 0.18:
                    should_fallback_to_web = True
                else:
                    should_fallback_to_web = False

            if should_fallback_to_web:
                web_context, source_urls = google_search_context(query, num_results=3)

                if web_context:
                    web_prompt = f"""
                    You are a helpful AI assistant.

                    The uploaded document does not contain this answer.
                    Use the web context below to answer the user's question clearly.
                    End your answer with a short "Sources" list using the source URLs.
                    Do NOT include internal reasoning or meta commentary.

                    Web Context:
                    {web_context}

                    Question:
                    {query}
                    """

                    web_response = llm.invoke(web_prompt)
                    final_answer = f"{no_data_message}\n\n{web_response.content}"
                else:
                    final_answer = (
                        f"{no_data_message}\n\n"
                        "I could not fetch useful results from Google right now. "
                        "Please try again in a moment."
                    )

            # Store response
            st.session_state.last_response = final_answer
            st.session_state.chat_history.append(
                {
                    "question": query,
                    "answer": final_answer,
                }
            )

            # Rerun to show response
            st.rerun()

    # =========================
    # SHOW CHAT HISTORY
    # =========================
    if st.session_state.chat_history:
        st.markdown("## � Chat History")

        for chat in st.session_state.chat_history:
            st.markdown(
                f"""
                <div style="
                    padding: 12px 18px;
                    margin: 15px 0;
                    background: rgba(168,85,247,0.15);
                    border-left: 3px solid #a855f7;
                    border-radius: 0 5px 5px 0;
                    color: #e9d5ff;
                    font-size: 15px;
                ">
                    <strong>Q:</strong> {chat['question']}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="response-box">
                    {chat['answer']}
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================
    # CHAT CONTAINER END
    # =========================
    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

# =========================
# FOOTER
# =========================
st.markdown(
    """
    <div class="footer">
        This RAG Bot is currently under active development.<br>
        Some features may still be improving during this phase.<br>
        Your feedback and support are greatly appreciated
    </div>
    """,
    unsafe_allow_html=True
)
