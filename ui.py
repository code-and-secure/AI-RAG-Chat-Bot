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
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
            <div style="font-size:24px; color: #00a67e;">✨</div>
            <h3 style="margin:0; font-weight:600; color: #333;">My bots</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input("Search in chats", label_visibility="collapsed", placeholder="🔍 Search in chats")
        
        st.markdown("""
        <div class="sidebar-item">📁 My bots</div>
        <div class="sidebar-item">👥 Public bots</div>
        <div class="sidebar-item">🔌 Integrations <span style="font-size:10px; color:#00a67e; background: #e0f2f1; padding: 2px 5px; border-radius: 4px;">Beta</span></div>
        <div class="sidebar-item active">💬 Chat</div>
        """, unsafe_allow_html=True)

def render_hero():
    avatar_b64 = get_base64_image("assets/avatar.png")
    template_path = os.path.join("templates", "welcome_screen.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        # Inject the base64 image into the placeholder
        st.markdown(template.format(avatar_b64=avatar_b64), unsafe_allow_html=True)
