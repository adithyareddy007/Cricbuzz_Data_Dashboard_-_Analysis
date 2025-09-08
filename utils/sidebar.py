import streamlit as st

def render_sidebar(page_name: str = None):
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/cricket.png", width=50)  # cricket icon
        st.markdown("## 🏏 Cricbuzz LiveStats")
        st.markdown("---")

        
