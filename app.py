import os
import json
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ui import load_css, render_sidebar, render_hero
from rag import process_document
from search import google_search_context, fetch_page_text

# =========================
# LOAD ENV & CONFIG
# =========================
load_dotenv()

STATS_FILE = "stats.json"

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_queries": 0, "total_docs": 0, "total_bots": 0}

def update_stat(key, increment=1):
    stats = load_stats()
    stats[key] = stats.get(key, 0) + increment
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

st.set_page_config(
    page_title="DocuMind",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# INITIALIZE SESSION STATE
# =========================
if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat"
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
if "show_fallback_popup" not in st.session_state:
    st.session_state.show_fallback_popup = False

# Load custom CSS
load_css()

# Render UI Sidebar Navigation
render_sidebar()

# Page Routing Configuration
current_page = st.session_state.current_page

# Helper to load mock documents into vector store
def load_mock_bot_data(bot_name, mock_texts, source_name):
    with st.spinner(f"Configuring {bot_name}..."):
        docs = [Document(page_content=text, metadata={"source": source_name}) for text in mock_texts]
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        db = Chroma.from_documents(docs, embeddings)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        
        st.session_state.docs = docs
        st.session_state.vector_db = db
        st.session_state.retriever = retriever
        st.session_state.file_uploaded = True
        st.session_state.uploaded_file_name = f"{bot_name} (Preloaded)"
        st.session_state.chat_history = []
        st.session_state.current_page = "Chat"
        st.rerun()

# ==================================================
# CHAT PAGE
# ==================================================
if current_page == "Chat":
    render_hero("Empower Your Future with <span>DocuMind</span> Solutions")

    # 1. FILE UPLOADER
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
                update_stat("total_bots", 1)
                update_stat("total_docs", 1)
                st.rerun()
    else:
        # File info display
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"📁 **Loaded Source:** `{st.session_state.uploaded_file_name}` ({len(st.session_state.docs)} chunks)")
        with col2:
            if st.button("Reset / Upload New", key="upload_new_btn", use_container_width=True):
                st.session_state.file_uploaded = False
                st.session_state.docs = []
                st.session_state.retriever = None
                st.session_state.vector_db = None
                st.session_state.uploaded_file_name = None
                st.session_state.submitted_query = ""
                st.session_state.last_response = ""
                st.session_state.chat_history = []
                st.rerun()

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 2. CHAT INPUT FORM
    with st.form(key="search_form", clear_on_submit=False):
        query_col1, query_col2 = st.columns([6, 1])
        with query_col1:
            query = st.text_input(
                "New chat in DocuMind",
                key="query_input",
                placeholder="Ask DocuMind anything... 📎",
                label_visibility="collapsed"
            )
        with query_col2:
            search_clicked = st.form_submit_button("Send", use_container_width=True)

    # 3. QUERY PROCESSING
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
            2) Keep the answer clean, final, and user-facing. Do not include internal thoughts, reasoning processes, phrases like "Okay, let me check", or any intermediate steps.
            3) Provide direct, concise answers without conversational filler.
            4) If context does not contain the answer, reply exactly: "I could not find this in the uploaded document."

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
                if "I could not find this in the uploaded document." in response.content:
                    should_fallback_to_web = True
                else:
                    should_fallback_to_web = False

            if should_fallback_to_web:
                st.session_state.show_fallback_popup = True
                web_context, source_urls = google_search_context(query, num_results=3)
                if web_context:
                    web_prompt = f"""
                    You are a helpful AI assistant.
                    The uploaded document does not contain this answer. Use the web context below to provide an accurate but short and simple answer.
                    Do not include any conversational fillers like "Okay", "Let me see", or internal reasoning. Just give the final answer directly.
                    End your answer with a short "Sources" list using the source URLs.

                    Web Context:
                    {web_context}

                    Question:
                    {query}
                    """
                    web_response = llm.invoke(web_prompt)
                    final_answer = f"{web_response.content}"
                else:
                    final_answer = "Could not fetch results from Google."

            st.session_state.last_response = final_answer
            st.session_state.chat_history.append({"question": query, "answer": final_answer})
            update_stat("total_queries", 1)
            st.rerun()

    # 4. CHAT HISTORY RENDER
    if st.session_state.show_fallback_popup:
        st.toast("Answer does not exist in the loaded document. Provided answer from Google.", icon="⚠️")
        st.session_state.show_fallback_popup = False

    if st.session_state.chat_history:
        st.markdown("---")
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"<div class='response-box'>{chat['answer']}</div>", unsafe_allow_html=True)

# ==================================================
# MY BOTS PAGE
# ==================================================
elif current_page == "My bots":
    render_hero("Your Personal <span>Bots</span> Library")
    
    st.markdown("### Manage Your AI Assistants")
    st.markdown("Here you can access the bots you've customized or files you've uploaded. (Currently displaying local session active bot).")

    if st.session_state.file_uploaded:
        st.success(f"✅ Active Bot: **{st.session_state.uploaded_file_name}**")
        st.markdown(f"**Chunks Indexed:** {len(st.session_state.docs)}")
        
        if st.button("💬 Chat with this Bot", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()
    else:
        st.info("No active custom bot found in this session. Head to the **Chat** page to upload a document and create one!")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Bot Statistics")
    
    stats = load_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Custom Bots", value=f"{stats['total_bots']}")
    with col2:
        st.metric(label="Total Queries Answered", value=f"{stats['total_queries']}")
    with col3:
        st.metric(label="Total Documents Indexed", value=f"{stats['total_docs']}")

# ==================================================
# PUBLIC BOTS PAGE
# ==================================================
elif current_page == "Public bots":
    render_hero("Choose a Pre-Configured Assistant")
    
    st.markdown("""
    <div class='page-intro'>
        Instantly chat with preloaded domain-specific assistants without uploading any files.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Bot 1: FinanceAI
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-icon">📈</div>
            <div class="card-title">FinanceAI</div>
            <div class="card-desc">Preloaded with Tesla (TSLA) Q4 2025 financial statements. Perfect for checking revenues, margins, and Cybertruck deliveries.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Activate FinanceAI", key="activate_finance", use_container_width=True):
            load_mock_bot_data(
                "FinanceAI",
                [
                    "Tesla Q4 2025 Financial Summary: Total revenues grew 14% year-over-year to $25.5 Billion. GAAP operating margin stood at 18.2%. cybertruck deliveries reached an all-time high of 150,000 units.",
                    "Tesla cash and cash equivalents grew by $2.3B to $28.1B at the end of fiscal year 2025. Energy generation and storage revenue hit a record $2.1B."
                ],
                "Tesla_Q4_2025.pdf"
            )

    # Bot 2: HR Policy Advisor
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-icon">👥</div>
            <div class="card-title">HR Policy Advisor</div>
            <div class="card-desc">Know your employee rights. Pre-trained with sample corporate policy on health insurance, PTO days, and remote work guidelines.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Activate HR Policy", key="activate_hr", use_container_width=True):
            load_mock_bot_data(
                "HR Advisor",
                [
                    "Employee Benefits Policy: Standard Paid Time Off (PTO) is 20 days per calendar year. Healthcare insurance premium is 100% covered by the company for full-time employees.",
                    "Remote Work Policy: Standard remote working hours are 9:00 AM to 6:00 PM. Employees are requested to core collaborate between 11:00 AM and 3:00 PM."
                ],
                "Employee_Handbook_2026.pdf"
            )

    # Bot 3: Legal NDA Assistant
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-icon">⚖️</div>
            <div class="card-title">Legal NDA Advisor</div>
            <div class="card-desc">Check contract clauses instantly. Preloaded with standard Non-Disclosure Agreement templates and jurisdiction details.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Activate Legal Advisor", key="activate_legal", use_container_width=True):
            load_mock_bot_data(
                "Legal Advisor",
                [
                    "Non-Disclosure Agreement: The term of this Agreement shall be 3 years from the Effective Date. The receiving party agrees to safeguard all proprietary confidential data.",
                    "Governing Law: This NDA and all conflicts arising hereunder shall be strictly governed by and construed in accordance with the laws of the State of Delaware."
                ],
                "Standard_NDA_Template.pdf"
            )

# ==================================================
# INTEGRATIONS PAGE (BETA)
# ==================================================
elif current_page == "Integrations":
    render_hero("Connect Your Workspace")
    
    st.markdown("""
    <div class='page-intro'>
        Connect DocuMind to your tools to ingest documents directly or interact via chat channels.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-icon">🕸️</div>
            <div class="card-title">Website Scraper & Crawler</div>
            <div class="card-desc">Enter any website URL to scrape its readable text, train the RAG vector DB, and start chatting about it instantly!</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Real working crawler implementation!
        crawl_url = st.text_input("Target URL", placeholder="https://example.com", label_visibility="collapsed")
        if st.button("Crawl & Train", key="crawl_btn", use_container_width=True):
            if crawl_url:
                with st.spinner("Scraping webpage and building database..."):
                    scraped_text = fetch_page_text(crawl_url, max_chars=8000)
                    if scraped_text:
                        # Split and process scraped content
                        splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
                        temp_doc = Document(page_content=scraped_text, metadata={"source": crawl_url})
                        docs = splitter.split_documents([temp_doc])

                        embeddings = HuggingFaceEmbeddings(
                            model_name="sentence-transformers/all-MiniLM-L6-v2",
                            model_kwargs={"device": "cpu"},
                            encode_kwargs={"normalize_embeddings": True},
                        )
                        db = Chroma.from_documents(docs, embeddings)
                        
                        st.session_state.docs = docs
                        st.session_state.vector_db = db
                        st.session_state.retriever = db.as_retriever(search_kwargs={"k": 3})
                        st.session_state.file_uploaded = True
                        st.session_state.uploaded_file_name = f"Scraped: {crawl_url}"
                        st.session_state.chat_history = []
                        st.session_state.current_page = "Chat"
                        st.success("Trained successfully! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Failed to scrape text. Ensure the URL is valid and public.")
            else:
                st.warning("Please enter a valid URL first!")

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-icon">💬</div>
            <div class="card-title">Slack Integration</div>
            <div class="card-desc">Deploy your RAG bot as a custom Slack app. Let your team query documents directly via channels or DM chats.</div>
        </div>
        """, unsafe_allow_html=True)
        slack_token = st.text_input("Slack Bot Token", placeholder="xoxb-xxxx-xxxx", type="password", label_visibility="collapsed")
        if st.button("Enable Slack Bot", key="slack_btn", use_container_width=True):
            if slack_token:
                st.success("Slack Bot verified and connected successfully! (Mock)")
            else:
                st.warning("Please enter a token first!")

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-icon">🤖</div>
            <div class="card-title">Google Drive Sync</div>
            <div class="card-desc">Automatically fetch, index, and continuously sync documents from specified folders inside your Google Drive account.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Connect Google Drive", key="gdrive_btn", use_container_width=True):
            st.info("Google OAuth login would trigger here. (Future Roadmap)")

    with col4:
        st.markdown("""
        <div class="card">
            <div class="card-icon">📓</div>
            <div class="card-title">Notion Integration</div>
            <div class="card-desc">Connect Notion API to index workspace pages. Query documentation databases directly from the chat interface.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Connect Notion", key="notion_btn", use_container_width=True):
            st.info("Notion Integrations portal would open here. (Future Roadmap)")
