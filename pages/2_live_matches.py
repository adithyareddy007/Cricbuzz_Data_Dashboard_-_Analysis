import streamlit as st
import pandas as pd
from utils.db_connection import get_connection
from sqlalchemy import text

# Page Config
st.set_page_config(page_title="Live Matches | Cricbuzz LiveStats", layout="wide")

# Sidebar
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: Live Matches")

st.title("⚡ Live Cricket Matches")

# Function to fetch live matches
def fetch_live_matches():
    query = """
        SELECT
            m.match_id,
            m.match_description,
            m.match_date,
            STRING_AGG(
                t.team_name || ' ' ||
                COALESCE(s.runs::text, '-') || '/' ||
                COALESCE(s.wickets::text, '-') || ' (' ||
                COALESCE(s.overs::text, '-') || ' ov)', ' | '
            ) AS scores
        FROM matches m
        LEFT JOIN match_scores s ON m.match_id = s.match_id
        LEFT JOIN teams t ON s.team_id = t.team_id
        GROUP BY m.match_id, m.match_description, m.match_date
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

# Display live matches
df = fetch_live_matches()
if df.empty:
    st.warning("No live matches found in database.")
else:
    # Format date nicely
    df['match_date'] = pd.to_datetime(df['match_date']).dt.strftime('%d-%b-%Y')
    st.dataframe(df, use_container_width=True)
