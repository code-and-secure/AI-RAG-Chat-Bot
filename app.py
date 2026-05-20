import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from ui import load_css, render_sidebar, render_hero
from rag import process_document
from search import google_search_context

# =========================
# LOAD ENV & CONFIG
# =========================
load_dotenv()

st.set_page_config(
    page_title="NameBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Render UI components
render_sidebar()
render_hero()

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
# FILE UPLOADER
# =========================
st.markdown("<div style='max-width:800px; margin: 0 auto;'>", unsafe_allow_html=True)
if not st.session_state.file_uploaded:
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, DOCX",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 1:
            st.warning("Only single documents are supported right now.")
            st.stop()

        uploaded_file = uploaded_files[0]
        with st.spinner("Processing document..."):
            docs, db, retriever = process_document(uploaded_file)
            st.session_state.docs = docs
            st.session_state.vector_db = db
            st.session_state.retriever = retriever
            st.session_state.file_uploaded = True
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.submitted_query = ""
            st.session_state.last_response = ""
            st.session_state.chat_history = []
            st.rerun()
else:
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"**Loaded:** {st.session_state.uploaded_file_name} ({len(st.session_state.docs)} chunks)")
    with col2:
        if st.button("Upload New", key="upload_new_btn"):
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
# CHAT INPUT
# =========================
with st.form(key="search_form", clear_on_submit=False):
    query_col1, query_col2 = st.columns([5, 1])
    with query_col1:
        query = st.text_input(
            "New chat in NameBot",
            key="query_input",
            placeholder="New chat in NameBot 📎",
            label_visibility="collapsed"
        )
    with query_col2:
        search_clicked = st.form_submit_button("Send", use_container_width=True)

# =========================
# PROCESS QUERY
# =========================
if query and search_clicked:
    st.session_state.submitted_query = query
    with st.spinner("AI is thinking..."):
        normalized_query = query.strip().lower()

        relevant_docs = []
        best_score = 0.0
        if st.session_state.vector_db is not None:
            try:
                scored_docs = st.session_state.vector_db.similarity_search_with_relevance_scores(normalized_query, k=4)
                if scored_docs:
                    best_score = scored_docs[0][1]
                    relevant_docs = [doc for doc, _ in scored_docs[:5]]
            except Exception:
                pass
        
        if not relevant_docs and st.session_state.retriever:
            relevant_docs = st.session_state.retriever.invoke(normalized_query)

        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        prompt = f"""
        You are a helpful AI assistant.
        Rules:
        1) Answer using only the context below.
        2) Keep the answer clean, final, and user-facing.
        3) If context does not contain the answer, reply exactly: "I could not find this in the uploaded document."

        Context:
        {context}

        Question:
        {query}
        """

        if not os.getenv("GROQ_API_KEY"):
            st.error("GROQ_API_KEY is missing. Add it to your .env file.")
            st.stop()

        llm = ChatGroq(model="qwen/qwen3-32b", temperature=0.3)

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
                The uploaded document does not contain this answer. Use the web context below.
                End your answer with a short "Sources" list using the source URLs.

                Web Context:
                {web_context}

                Question:
                {query}
                """
                web_response = llm.invoke(web_prompt)
                final_answer = f"Searching web...\n\n{web_response.content}"
            else:
                final_answer = "Could not fetch results from Google."

        st.session_state.last_response = final_answer
        st.session_state.chat_history.append({"question": query, "answer": final_answer})
        st.rerun()

# =========================
# SHOW CHAT HISTORY
# =========================
if st.session_state.chat_history:
    st.markdown("---")
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {chat['question']}")
        st.markdown(f"<div class='response-box'>{chat['answer']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
