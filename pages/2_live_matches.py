import streamlit as st
import pandas as pd
from utils.db_connection import get_connection
from sqlalchemy import text
import time
from datetime import datetime

# Page Config
st.set_page_config(page_title="Live Matches | Cricbuzz LiveStats", layout="wide", page_icon="⚡")

# Custom CSS
st.markdown("""
<style>
    .match-card {
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    .live-indicator {
        background: #ff4444;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .score-highlight {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: Live Matches")
st.sidebar.markdown("---")

# Auto-refresh option
auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (30s)", value=False)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 10, 120, 30)

if st.sidebar.button("🔄 Manual Refresh"):
    st.rerun()

# Main title with live indicator
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("⚡ Live Cricket Matches")
with col3:
    st.markdown(f"<div class='live-indicator'>🔴 LIVE</div>", unsafe_allow_html=True)

# Function to fetch live matches with enhanced details
def fetch_live_matches():
    query = """
        SELECT
            m.match_id,
            m.match_description,
            m.match_date,
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
        GROUP BY m.match_id, m.match_description, m.match_date, v.venue_name, v.city
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

# Function to get match statistics
def get_match_stats():
    conn = get_connection()
    if not conn:
        return 0, 0, 0
    
    try:
        # Total matches today
        today_matches = conn.execute(text("""
            SELECT COUNT(*) FROM matches 
            WHERE match_date = CURRENT_DATE
        """)).fetchone()[0]
        
        # Live matches (with scores)
        live_matches = conn.execute(text("""
            SELECT COUNT(DISTINCT match_id) FROM match_scores 
            WHERE runs > 0
        """)).fetchone()[0]
        
        # Total runs scored today
        total_runs = conn.execute(text("""
            SELECT COALESCE(SUM(runs), 0) FROM match_scores ms
            JOIN matches m ON ms.match_id = m.match_id
            WHERE m.match_date = CURRENT_DATE
        """)).fetchone()[0]
        
        return today_matches, live_matches, total_runs
    except:
        return 0, 0, 0
    finally:
        conn.close()

# Display statistics
col1, col2, col3, col4 = st.columns(4)
today_matches, live_matches, total_runs = get_match_stats()

with col1:
    st.metric("📅 Today's Matches", today_matches)
with col2:
    st.metric("🔴 Live Matches", live_matches)
with col3:
    st.metric("🏃 Total Runs", total_runs)
with col4:
    st.metric("⏰ Last Updated", datetime.now().strftime("%H:%M:%S"))

st.markdown("---")

# Fetch and display matches
with st.spinner("🔄 Fetching live matches..."):
    df = fetch_live_matches()

if df.empty:
    st.warning("📭 No live matches found in database.")
    st.info("💡 **Tip**: Run `python etl_load.py` to fetch the latest match data from Cricbuzz API.")
else:
    # Format the data for better display
    df['match_date'] = pd.to_datetime(df['match_date']).dt.strftime('%d %b %Y')
    
    # Add match status based on whether there are scores
    df['status'] = df['teams_batting'].apply(
        lambda x: '🔴 LIVE' if x > 0 else '📅 SCHEDULED'
    )
    
    # Display matches as cards
    st.subheader(f"📊 Found {len(df)} matches")
    
    for idx, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4>{row['match_description']}</h4>
                        <span class="{'live-indicator' if '🔴' in row['status'] else ''}">{row['status']}</span>
                    </div>
                    <p><strong>📍 Venue:</strong> {row['venue_name'] or 'TBD'}, {row['city'] or ''}</p>
                    <p><strong>📅 Date:</strong> {row['match_date']}</p>
                    <div class="score-highlight">
                        <strong>🏏 Scores:</strong> {row['scores'] or 'Not started yet'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"📊 Details", key=f"details_{idx}"):
                    st.info(f"Match ID: {row['match_id']}")
    
    # Display as table option
    if st.checkbox("📋 View as Table"):
        display_df = df[['match_description', 'venue_name', 'city', 'match_date', 'scores', 'status']].copy()
        display_df.columns = ['Match', 'Venue', 'City', 'Date', 'Scores', 'Status']
        st.dataframe(display_df, use_container_width=True)

# Footer with last update time
st.markdown("---")
st.markdown(f"*Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
st.markdown("*Data fetched from Cricbuzz API*")

# Auto-refresh functionality
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()