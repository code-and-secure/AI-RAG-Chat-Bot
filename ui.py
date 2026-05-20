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
            <div class="sidebar-brand-mark">DM</div>
            <div>
                <div class="sidebar-brand-name">DocuMind</div>
                <div class="sidebar-brand-subtitle">Think. Execute. Repeat.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input("Search in chats", label_visibility="collapsed", placeholder="🔍 Search in chats")
        
        # Initialize page state if not exists
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Chat"

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Render active navigation styling using CSS variables for fully adaptive look
        active_page = st.session_state.current_page
        active_css = ""
        if active_page == "Chat":
            active_css = "div[data-testid='stSidebar'] button[key='nav_chat'] { background: linear-gradient(135deg, rgba(255, 109, 63, 0.24), rgba(90, 255, 196, 0.18)) !important; border: 1px solid rgba(255,255,255,0.12) !important; font-weight: 600 !important; color: #f5f7fb !important; box-shadow: 0 16px 32px rgba(0,0,0,0.28) !important; }"
        elif active_page == "My bots":
            active_css = "div[data-testid='stSidebar'] button[key='nav_my_bots'] { background: linear-gradient(135deg, rgba(255, 109, 63, 0.24), rgba(90, 255, 196, 0.18)) !important; border: 1px solid rgba(255,255,255,0.12) !important; font-weight: 600 !important; color: #f5f7fb !important; box-shadow: 0 16px 32px rgba(0,0,0,0.28) !important; }"
        elif active_page == "Public bots":
            active_css = "div[data-testid='stSidebar'] button[key='nav_public_bots'] { background: linear-gradient(135deg, rgba(255, 109, 63, 0.24), rgba(90, 255, 196, 0.18)) !important; border: 1px solid rgba(255,255,255,0.12) !important; font-weight: 600 !important; color: #f5f7fb !important; box-shadow: 0 16px 32px rgba(0,0,0,0.28) !important; }"
        elif active_page == "Integrations":
            active_css = "div[data-testid='stSidebar'] button[key='nav_integrations'] { background: linear-gradient(135deg, rgba(255, 109, 63, 0.24), rgba(90, 255, 196, 0.18)) !important; border: 1px solid rgba(255,255,255,0.12) !important; font-weight: 600 !important; color: #f5f7fb !important; box-shadow: 0 16px 32px rgba(0,0,0,0.28) !important; }"
            
        st.markdown(f"<style>{active_css}</style>", unsafe_allow_html=True)

        # Interactive sidebar buttons
        if st.button("💬 Chat", key="nav_chat", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()

        if st.button("📁 My bots", key="nav_my_bots", use_container_width=True):
            st.session_state.current_page = "My bots"
            st.rerun()

        if st.button("👥 Public bots", key="nav_public_bots", use_container_width=True):
            st.session_state.current_page = "Public bots"
            st.rerun()

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
        rendered_template = template.replace("{avatar_b64}", avatar_b64).replace("Hello, how can I help today?", title)
        st.markdown(rendered_template, unsafe_allow_html=True)
