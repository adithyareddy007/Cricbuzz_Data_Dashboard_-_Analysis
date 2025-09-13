import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pandas as pd
from utils.db_connection import get_connection
from sqlalchemy import text
import time

# Page Config
st.set_page_config(page_title="Top Stats | Cricbuzz LiveStats", layout="wide", page_icon="📊")

# Custom CSS
st.markdown("""
<style>
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .category-selector {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: Top Stats")
st.sidebar.markdown("---")

# Show database stats in sidebar
def show_db_stats():
    conn = get_connection()
    if conn:
        try:
            batting_count = conn.execute(text("SELECT COUNT(*) FROM batting_stats")).fetchone()[0]
            bowling_count = conn.execute(text("SELECT COUNT(*) FROM bowling_stats")).fetchone()[0]
            players_count = conn.execute(text("SELECT COUNT(*) FROM players")).fetchone()[0]
            
            st.sidebar.markdown("📈 **Database Stats:**")
            st.sidebar.metric("Players", players_count)
            st.sidebar.metric("Batting Records", batting_count)
            st.sidebar.metric("Bowling Records", bowling_count)
        except Exception as e:
            st.sidebar.error(f"Error fetching DB stats: {e}")
        finally:
            conn.close()

show_db_stats()

# Main title
st.title("📊 Top Player Statistics")
st.markdown("*Real-time cricket player statistics from Cricbuzz API*")

# DB connection function with better error handling
def get_db_connection():
    try:
        from sqlalchemy import create_engine
        engine = create_engine("postgresql+psycopg2://postgres:adi1234@localhost:5432/cricbuzz_db")
        return engine.connect()
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# Load API key with validation
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")

if not API_KEY:
    st.error("❌ **API Configuration Missing**")
    st.markdown("""
    **Setup Instructions:**
    1. Create a `.env` file in your project root
    2. Add your RapidAPI key: `RAPIDAPI_KEY=your_key_here`
    3. Get your API key from [RapidAPI Cricbuzz](https://rapidapi.com/cricapi/api/cricbuzz-cricket/)
    """)
    st.stop()

headers = {
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

# Test API connection
def test_api_connection():
    try:
        test_url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats"
        response = requests.get(test_url, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

# API Status indicator
col1, col2 = st.columns([3, 1])
with col2:
    if test_api_connection():
        st.success("🟢 API Connected")
    else:
        st.error("🔴 API Error")
        st.warning("Check your API key and internet connection")

# Main content
with st.container():
    st.markdown('<div class="category-selector">', unsafe_allow_html=True)
    
    # Configuration section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_choice = st.selectbox(
            "📊 **Select Category**", 
            ["Batting", "Bowling"],
            help="Choose between batting or bowling statistics"
        )
    
    with col2:
        format_choice = st.selectbox(
            "🏏 **Select Format**", 
            ["test", "odi", "t20"],
            help="Cricket format: Test, ODI, or T20"
        )
    
    with col3:
        limit_choice = st.selectbox(
            "🔢 **Show Top**",
            [5, 10, 15, 20],
            index=1,
            help="Number of players to display"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Fetch stat types with caching and error handling
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stat_types():
    try:
        stats_url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats"
        response = requests.get(stats_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return []
        
        stats_data = response.json().get("statsTypesList", [])
        stat_types = []
        
        for category in stats_data:
            for t in category["types"]:
                stat_types.append({
                    "value": t["value"],
                    "label": t["header"],
                    "category": t["category"]
                })
        
        return stat_types
    except requests.exceptions.Timeout:
        st.error("⏰ API request timed out. Please try again.")
        return []
    except Exception as e:
        st.error(f"❌ Error fetching stat types: {e}")
        return []

# Load stat types
with st.spinner("🔄 Loading available statistics..."):
    stat_types = fetch_stat_types()

if not stat_types:
    st.error("Unable to load statistics. Please check your API connection.")
    st.stop()

# Filter stat types by selected category
filtered_stats = [t for t in stat_types if category_choice.lower() in t["category"].lower()]

if not filtered_stats:
    st.warning(f"No statistics available for {category_choice}")
    st.stop()

# Stat type selection
stat_choice = st.selectbox(
    f"📈 **Select {category_choice} Statistic**",
    [f"{t['label']}" for t in filtered_stats],
    help="Choose the specific statistic to view"
)

stat_value = next(
    (t["value"] for t in filtered_stats if t["label"] == stat_choice),
    "mostRuns"
)

# Fetch and display data
if st.button("📊 **Load Statistics**", type="primary"):
    with st.spinner(f"🔄 Fetching {stat_choice} for {format_choice.upper()}..."):
        try:
            # Fetch leaderboard
            top_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0?statsType={stat_value}"
            response = requests.get(top_url, headers=headers, params={"formatType": format_choice}, timeout=15)
            
            if response.status_code != 200:
                st.error(f"❌ API Error {response.status_code}: {response.text}")
                st.stop()
            
            data = response.json()
            headers_list = data.get("headers", [])
            players = data.get("values", [])
            
            if not players:
                st.warning("📭 No data available for this statistic.")
                st.stop()
            
            # Process data
            values_list = [p["values"] for p in players]
            
            # Fix header/value mismatch
            if len(headers_list) < len(values_list[0]):
                headers_list += [f"Extra_{i}" for i in range(len(headers_list), len(values_list[0]))]
            
            df = pd.DataFrame(values_list, columns=headers_list)
            
            # Display results
            st.success(f"✅ Loaded {len(df)} records")
            
            # Statistics summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="stat-card"><h3>{stat_choice}</h3><p>{format_choice.upper()} Format</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><h3>{len(df[:limit_choice])}</h3><p>Top Players</p></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-card"><h3>{category_choice}</h3><p>Statistics</p></div>', unsafe_allow_html=True)
            
            # Display table
            st.subheader(f"🏆 Top {limit_choice} - {stat_choice} ({format_choice.upper()})")
            
            # Add ranking column
            display_df = df.head(limit_choice).copy()
            display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
            
            st.dataframe(
                display_df, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("🏆", width="small")
                }
            )
            
            # Save to database
            conn = get_db_connection()
            if conn:
                try:
                    saved_count = 0
                    
                    for p in players[:limit_choice]:
                        player_name = p["values"][0]
                        matches = None
                        value = None
                        
                        # Extract matches and primary stat value
                        for idx, col in enumerate(headers_list):
                            if "Mat" in col or "Matches" in col:
                                try:
                                    matches = int(p["values"][idx])
                                except:
                                    matches = 0
                            elif idx == 1:  # Usually the main stat is in second column
                                try:
                                    value = int(str(p["values"][idx]).replace('*', '').replace(',', ''))
                                except:
                                    value = 0
                        
                        # Insert/update player
                        conn.execute(
                            text("""
                            INSERT INTO players (name, matches)
                            VALUES (:name, :matches)
                            ON CONFLICT (name) DO UPDATE SET 
                                matches = COALESCE(EXCLUDED.matches, players.matches)
                            """),
                            {"name": player_name, "matches": matches or 0}
                        )
                        
                        # Get player_id
                        result = conn.execute(
                            text("SELECT player_id FROM players WHERE name = :name"),
                            {"name": player_name}
                        ).fetchone()
                        
                        if result and value is not None:
                            player_id = result[0]
                            
                            # Insert stats based on category
                            if category_choice == "Batting":
                                conn.execute(
                                    text("""
                                    INSERT INTO batting_stats (player_id, format, stat_type, value, matches)
                                    VALUES (:pid, :fmt, :stat, :val, :matches)
                                    ON CONFLICT (player_id, format, stat_type) DO UPDATE
                                    SET value = EXCLUDED.value, matches = EXCLUDED.matches
                                    """),
                                    {"pid": player_id, "fmt": format_choice, "stat": stat_value, "val": value, "matches": matches or 0}
                                )
                            else:
                                conn.execute(
                                    text("""
                                    INSERT INTO bowling_stats (player_id, format, stat_type, value, matches)
                                    VALUES (:pid, :fmt, :stat, :val, :matches)
                                    ON CONFLICT (player_id, format, stat_type) DO UPDATE
                                    SET value = EXCLUDED.value, matches = EXCLUDED.matches
                                    """),
                                    {"pid": player_id, "fmt": format_choice, "stat": stat_value, "val": value, "matches": matches or 0}
                                )
                            
                            saved_count += 1
                    
                    conn.commit()
                    st.success(f"✅ Saved {saved_count} player records to database")
                    
                except Exception as e:
                    st.error(f"❌ Database save error: {e}")
                    conn.rollback()
                finally:
                    conn.close()
            
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")

# Footer
st.markdown("---")
st.markdown("*Data provided by Cricbuzz API via RapidAPI*")