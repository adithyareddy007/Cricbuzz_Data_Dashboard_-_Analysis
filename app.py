import streamlit as st

# Page Config
st.set_page_config(page_title="Cricbuzz LiveStats Dashboard", layout="wide")

# Sidebar (self-contained, no utils)
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: Home")

# Main Content
st.title("🏏 Cricbuzz LiveStats")
st.markdown("""
Welcome to **Cricbuzz LiveStats**, a real-time cricket analytics dashboard.

👉 Use the sidebar to navigate:
- ⚡ Live Match Updates  
- 📊 Top Player Stats  
""")

