import base64
import os
import streamlit as st

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
            </div>
            <div>
                <div class="sidebar-brand-name">DocuMind</div>
                <div class="sidebar-brand-subtitle">Think. Execute. Repeat.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        search_query = st.text_input("Search in chats", label_visibility="collapsed", placeholder="🔍 Search in chats").lower()
        
        # Initialize page state if not exists
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Chat"

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Render active navigation styling using CSS variables for fully adaptive look
        active_page = st.session_state.current_page
        active_css = ""
        base_active = "background: var(--secondary-background-color) !important; border: 1px solid var(--primary-color) !important; font-weight: 700 !important; color: var(--primary-color) !important; opacity: 1 !important; box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;"
        if active_page == "Chat":
            active_css = "div[data-testid='stSidebar'] button[key='nav_chat'] { " + base_active + " }"
        elif active_page == "My bots":
            active_css = "div[data-testid='stSidebar'] button[key='nav_my_bots'] { " + base_active + " }"
        elif active_page == "Public bots":
            active_css = "div[data-testid='stSidebar'] button[key='nav_public_bots'] { " + base_active + " }"
        elif active_page == "Integrations":
            active_css = "div[data-testid='stSidebar'] button[key='nav_integrations'] { " + base_active + " }"
            
        st.markdown(f"<style>{active_css}</style>", unsafe_allow_html=True)

        # Interactive sidebar buttons
        if not search_query or search_query in "chat":
            if st.button("💬 Chat", key="nav_chat", use_container_width=True):
                st.session_state.current_page = "Chat"
                st.rerun()

        if not search_query or search_query in "my bots":
            if st.button("📁 My bots", key="nav_my_bots", use_container_width=True):
                st.session_state.current_page = "My bots"
                st.rerun()

        if not search_query or search_query in "public bots":
            if st.button("👥 Public bots", key="nav_public_bots", use_container_width=True):
                st.session_state.current_page = "Public bots"
                st.rerun()

        if not search_query or search_query in "integrations (beta)":
            if st.button("🔌 Integrations (Beta)", key="nav_integrations", use_container_width=True):
                st.session_state.current_page = "Integrations"
                st.rerun()

def render_hero(title="Hello, how can I help today?"):
    avatar_b64 = get_base64_image("assets/avatar.png")
    template_path = os.path.join("templates", "welcome_screen.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        # Dynamically inject title and avatar
        rendered_template = template.replace("{avatar_b64}", avatar_b64).replace("{{_TITLE_}}", str(title))
        st.markdown(rendered_template, unsafe_allow_html=True)
