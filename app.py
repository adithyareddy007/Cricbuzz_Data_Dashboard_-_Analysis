import streamlit as st
import pandas as pd
from utils.db_connection import get_connection
from sqlalchemy import text

# Page Config
st.set_page_config(
    page_title="Cricbuzz LiveStats Dashboard", 
    layout="wide",
    page_icon="🏏",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6B35;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation (Cleaned)
st.sidebar.markdown("🏏 **Cricbuzz LiveStats**")
st.sidebar.markdown("📌 **Navigation:**")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/2_live_matches.py", label="⚡ Live Matches", icon="⚡")
st.sidebar.page_link("pages/3_top_stats.py", label="📊 Top Stats", icon="📊")
st.sidebar.page_link("pages/curd_operations.py", label="🛠️ CRUD Operations", icon="🛠️")
st.sidebar.markdown("---")

# Quick Stats in Sidebar
def get_quick_stats():
    conn = get_connection()
    if not conn:
        return None, None, None
    
    try:
        matches_result = conn.execute(text("SELECT COUNT(*) FROM matches")).fetchone()
        total_matches = matches_result[0] if matches_result else 0
        
        players_result = conn.execute(text("SELECT COUNT(*) FROM players")).fetchone()
        total_players = players_result[0] if players_result else 0
        
        active_result = conn.execute(text("""
            SELECT COUNT(DISTINCT match_id) FROM match_scores 
            WHERE runs > 0
        """)).fetchone()
        active_matches = active_result[0] if active_result else 0
        
        return total_matches, total_players, active_matches
    except Exception as e:
        st.sidebar.error(f"Error fetching stats: {e}")
        return 0, 0, 0
    finally:
        conn.close()

matches, players, active = get_quick_stats()
if matches is not None:
    st.sidebar.markdown("📈 **Quick Stats:**")
    st.sidebar.metric("Total Matches", matches)
    st.sidebar.metric("Total Players", players)
    st.sidebar.metric("Active Matches", active)

# Main Header Only (removed feature cards)
st.markdown("""
<div class="main-header">
    <h1>🏏 Cricbuzz LiveStats Dashboard</h1>
    <p>Your one-stop destination for real-time cricket analytics</p>
</div>
""", unsafe_allow_html=True)

# Recent Activity Section
st.markdown("### 📈 Recent Activity")

def get_recent_matches():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT 
            m.match_description,
            m.match_date,
            COUNT(ms.match_id) as teams_with_scores
        FROM matches m
        LEFT JOIN match_scores ms ON m.match_id = ms.match_id
        GROUP BY m.match_id, m.match_description, m.match_date
        ORDER BY m.match_date DESC
        LIMIT 5
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching recent matches: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

recent_df = get_recent_matches()
if not recent_df.empty:
    st.dataframe(recent_df, use_container_width=True)
else:
    st.info("No recent match data available. Run the ETL pipeline to fetch latest matches.")

# Quick Actions
st.markdown("### 🚀 Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.info("To refresh data, run: `python etl_load.py`")

with col2:
    if st.button("📊 View Live Matches", use_container_width=True):
        st.switch_page("pages/2_live_matches.py")

with col3:
    if st.button("📊 SQL Analytics", use_container_width=True):
        st.switch_page("pages/4_sql_analytics.py")

# Footer
st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit and Cricbuzz API*")
