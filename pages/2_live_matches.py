import streamlit as st
import pandas as pd
from utils.db_connection import get_connection
from sqlalchemy import text
from datetime import datetime

# Page Config
st.set_page_config(page_title="Live Matches | Cricbuzz LiveStats", layout="wide", page_icon="⚡")

# Custom CSS → sync cards with dashboard theme
st.markdown("""
<style>
    .match-card {
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: var(--background-color); /* Streamlit theme background */
        color: var(--text-color); /* Streamlit theme text */
        box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
    }
    .match-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    .live-indicator {
        background: #ff4444;
        color: white;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: Live Matches")
st.sidebar.markdown("---")

# Main Header
col1, col2 = st.columns([4, 1])
with col1:
    st.title("⚡ Live Cricket Matches")
with col2:
    st.markdown("<div class='live-indicator'>🔴 LIVE</div>", unsafe_allow_html=True)

# Function to fetch live matches
def fetch_live_matches():
    query = """
        SELECT
            m.match_id,
            m.match_description,
            v.venue_name,
            v.city,
            STRING_AGG(
                t.team_name || ': ' ||
                COALESCE(s.runs::text, '0') || '/' ||
                COALESCE(s.wickets::text, '0') || ' (' ||
                COALESCE(s.overs::text, '0') || ' ov)', ' | '
                ORDER BY s.team_id
            ) AS scores,
            COUNT(s.match_id) as teams_batting
        FROM matches m
        LEFT JOIN match_scores s ON m.match_id = s.match_id
        LEFT JOIN teams t ON s.team_id = t.team_id
        LEFT JOIN venues v ON m.venue_id = v.venue_id
        GROUP BY m.match_id, m.match_description, v.venue_name, v.city
        HAVING COUNT(s.match_id) > 0  -- only show matches with scores
        ORDER BY m.match_date DESC
        LIMIT 20;
    """
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed.")
        return pd.DataFrame()

    try:
        result = conn.execute(text(query))
        rows = result.fetchall()
        colnames = result.keys()
        return pd.DataFrame(rows, columns=colnames) if rows else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Fetch and display matches
with st.spinner("🔄 Fetching live scores..."):
    df = fetch_live_matches()

if df.empty:
    st.warning("📭 No live matches currently.")
    st.info("💡 Tip: Run `python etl_load.py` to fetch the latest match data.")
else:
    # Display line by line as cards
    st.subheader(f"📊 {len(df)} Live Matches Found")
    for idx, row in df.iterrows():
        st.markdown(f"""
        <div class="match-card">
            <h4>{row['match_description']}</h4>
            <p><strong>📍 Venue:</strong> {row['venue_name'] or 'TBD'}, {row['city'] or ''}</p>
            <p><strong>🏏 Scores:</strong> {row['scores']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Optional toggle: Show as table
    if st.checkbox("📋 View as Table"):
        display_df = df[['match_description', 'venue_name', 'city', 'scores']].copy()
        display_df.columns = ['Match', 'Venue', 'City', 'Scores']
        st.dataframe(display_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"*Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
st.markdown("*Data fetched from Cricbuzz API*")
