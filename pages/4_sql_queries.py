import streamlit as st
import pandas as pd
from utils.db_connection_2 import get_connection
from sqlalchemy import text
import time
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="SQL Analytics | Cricbuzz LiveStats", 
    layout="wide", 
    page_icon="📊"
)

# Custom CSS
st.markdown("""
<style>
    .analytics-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #2a5298;
    }
    .difficulty-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .beginner { background: #d4edda; color: #155724; }
    .intermediate { background: #fff3cd; color: #856404; }
    .advanced { background: #f8d7da; color: #721c24; }
    .sql-code {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
    .result-summary {
        background: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #b8daff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: SQL Analytics")
st.sidebar.markdown("---")

# Quick navigation in sidebar
st.sidebar.markdown("🔍 **Quick Navigation:**")
difficulty_filter = st.sidebar.selectbox(
    "Filter by Difficulty:",
    ["All Queries", "Beginner (1-8)", "Intermediate (9-16)"]
)

# Database connection function
def execute_analytics_query(query, query_name):
    """Execute SQL query and return results with error handling"""
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed")
        return None
    
    try:
        start_time = time.time()
        result = conn.execute(text(query))
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        # Get column names and data
        columns = list(result.keys())
        rows = result.fetchall()
        
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.success(f"✅ Query executed successfully in {execution_time}ms")
            return df, execution_time
        else:
            st.warning("📭 No data returned by query")
            return None, execution_time
            
    except Exception as e:
        st.error(f"❌ Query failed: {str(e)}")
        return None, 0
    finally:
        conn.close()

# Main header
st.markdown("""
<div class="analytics-header">
    <h1>📊 SQL Queries & Analytics</h1>
    <p>Advanced cricket database analytics with 16 comprehensive queries</p>
</div>
""", unsafe_allow_html=True)

# Query definitions with metadata
ANALYTICS_QUERIES = {
    # BEGINNER LEVEL (1-8)
    1: {
        "title": "Players from India",
        "difficulty": "beginner",
        "description": "Find all players who represent India with their playing details",
        "sql": """
        SELECT 
            player_name AS "Full Name",
            playing_role AS "Playing Role",
            batting_style AS "Batting Style",
            bowling_style AS "Bowling Style"
        FROM players 
        WHERE country = 'India'
        ORDER BY player_name;
        """,
        "expected_columns": ["Full Name", "Playing Role", "Batting Style", "Bowling Style"]
    },
    
    2: {
        "title": "Recent Matches (Last 30 Days)",
        "difficulty": "beginner", 
        "description": "Show all cricket matches played in the last 30 days",
        "sql": """
        SELECT 
            m.match_description AS "Match Description",
            t1.team_name AS "Team 1",
            t2.team_name AS "Team 2",
            CONCAT(v.venue_name, ', ', v.city) AS "Venue",
            m.match_date AS "Match Date"
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.match_date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY m.match_date DESC;
        """,
        "expected_columns": ["Match Description", "Team 1", "Team 2", "Venue", "Match Date"]
    },
    
    3: {
        "title": "Top 10 ODI Run Scorers",
        "difficulty": "beginner",
        "description": "List the top 10 highest run scorers in ODI cricket",
        "sql": """
        SELECT 
            p.player_name AS "Player Name",
            SUM(bp.runs_scored) AS "Total Runs",
            ROUND(AVG(CASE WHEN bp.runs_scored > 0 THEN bp.runs_scored END), 2) AS "Batting Average",
            COUNT(CASE WHEN bp.runs_scored >= 100 THEN 1 END) AS "Centuries"
        FROM players p
        JOIN batting_performances bp ON p.player_id = bp.player_id
        JOIN matches m ON bp.match_id = m.match_id
        WHERE m.match_type = 'ODI'
        GROUP BY p.player_id, p.player_name
        HAVING SUM(bp.runs_scored) > 0
        ORDER BY SUM(bp.runs_scored) DESC
        LIMIT 10;
        """,
        "expected_columns": ["Player Name", "Total Runs", "Batting Average", "Centuries"]
    },
    
    4: {
        "title": "Large Capacity Venues",
        "difficulty": "beginner",
        "description": "Display venues with seating capacity > 50,000",
        "sql": """
        SELECT 
            venue_name AS "Venue Name",
            city AS "City",
            country AS "Country",
            capacity AS "Capacity"
        FROM venues 
        WHERE capacity > 50000
        ORDER BY capacity DESC;
        """,
        "expected_columns": ["Venue Name", "City", "Country", "Capacity"]
    },
    
    5: {
        "title": "Team Win Statistics",
        "difficulty": "beginner",
        "description": "Calculate total wins for each team",
        "sql": """
        SELECT 
            t.team_name AS "Team Name",
            COUNT(mr.winning_team_id) AS "Total Wins"
        FROM teams t
        LEFT JOIN match_results mr ON t.team_id = mr.winning_team_id
        GROUP BY t.team_id, t.team_name
        ORDER BY COUNT(mr.winning_team_id) DESC;
        """,
        "expected_columns": ["Team Name", "Total Wins"]
    },
    
    6: {
        "title": "Players by Role Distribution",
        "difficulty": "beginner",
        "description": "Count players in each playing role category",
        "sql": """
        SELECT 
            playing_role AS "Playing Role",
            COUNT(*) AS "Number of Players"
        FROM players 
        WHERE playing_role IS NOT NULL
        GROUP BY playing_role
        ORDER BY COUNT(*) DESC;
        """,
        "expected_columns": ["Playing Role", "Number of Players"]
    },
    
    7: {
        "title": "Format-wise Highest Scores",
        "difficulty": "beginner",
        "description": "Find highest individual batting score in each cricket format",
        "sql": """
        SELECT 
            m.match_type AS "Format",
            MAX(bp.runs_scored) AS "Highest Score"
        FROM batting_performances bp
        JOIN matches m ON bp.match_id = m.match_id
        GROUP BY m.match_type
        ORDER BY MAX(bp.runs_scored) DESC;
        """,
        "expected_columns": ["Format", "Highest Score"]
    },
    
    8: {
        "title": "2024 Cricket Series",
        "difficulty": "beginner",
        "description": "Show all cricket series that started in 2024",
        "sql": """
        SELECT 
            series_name AS "Series Name",
            host_country AS "Host Country",
            match_type AS "Match Type",
            start_date AS "Start Date",
            total_matches AS "Total Matches"
        FROM series 
        WHERE EXTRACT(YEAR FROM start_date) = 2024
        ORDER BY start_date;
        """,
        "expected_columns": ["Series Name", "Host Country", "Match Type", "Start Date", "Total Matches"]
    },

    # INTERMEDIATE LEVEL (9-16)
    9: {
        "title": "Elite All-Rounders Analysis",
        "difficulty": "intermediate",
        "description": "All-rounders with 1000+ runs AND 50+ wickets",
        "sql": """
        SELECT DISTINCT
            p.player_name AS "Player Name",
            SUM(bp.runs_scored) AS "Total Runs",
            SUM(bowl.wickets_taken) AS "Total Wickets",
            m.match_type AS "Format"
        FROM players p
        JOIN batting_performances bp ON p.player_id = bp.player_id
        JOIN bowling_performances bowl ON p.player_id = bowl.player_id AND bp.match_id = bowl.match_id
        JOIN matches m ON bp.match_id = m.match_id
        WHERE p.playing_role = 'All-rounder'
        GROUP BY p.player_id, p.player_name, m.match_type
        HAVING SUM(bp.runs_scored) > 1000 AND SUM(bowl.wickets_taken) > 50
        ORDER BY SUM(bp.runs_scored) DESC;
        """,
        "expected_columns": ["Player Name", "Total Runs", "Total Wickets", "Format"]
    },

    10: {
        "title": "Recent Match Results Analysis", 
        "difficulty": "intermediate",
        "description": "Details of last 20 completed matches with full results",
        "sql": """
        SELECT 
            m.match_description AS "Match Description",
            t1.team_name AS "Team 1",
            t2.team_name AS "Team 2",
            tw.team_name AS "Winning Team",
            mr.victory_margin AS "Victory Margin",
            mr.victory_type AS "Victory Type",
            v.venue_name AS "Venue"
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN match_results mr ON m.match_id = mr.match_id
        LEFT JOIN teams tw ON mr.winning_team_id = tw.team_id
        LEFT JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.status = 'Completed'
        ORDER BY m.match_date DESC
        LIMIT 20;
        """,
        "expected_columns": ["Match Description", "Team 1", "Team 2", "Winning Team", "Victory Margin", "Victory Type", "Venue"]
    },

    11: {
        "title": "Multi-Format Player Comparison",
        "difficulty": "intermediate", 
        "description": "Compare player performance across different cricket formats",
        "sql": """
        SELECT 
            p.player_name AS "Player Name",
            SUM(CASE WHEN m.match_type = 'Test' THEN bp.runs_scored ELSE 0 END) AS "Test Runs",
            SUM(CASE WHEN m.match_type = 'ODI' THEN bp.runs_scored ELSE 0 END) AS "ODI Runs", 
            SUM(CASE WHEN m.match_type = 'T20I' THEN bp.runs_scored ELSE 0 END) AS "T20I Runs",
            ROUND(AVG(bp.runs_scored), 2) AS "Overall Average"
        FROM players p
        JOIN batting_performances bp ON p.player_id = bp.player_id
        JOIN matches m ON bp.match_id = m.match_id
        WHERE p.player_id IN (
            SELECT player_id 
            FROM batting_performances bp2
            JOIN matches m2 ON bp2.match_id = m2.match_id
            GROUP BY player_id
            HAVING COUNT(DISTINCT m2.match_type) >= 2
        )
        GROUP BY p.player_id, p.player_name
        ORDER BY ROUND(AVG(bp.runs_scored), 2) DESC;
        """,
        "expected_columns": ["Player Name", "Test Runs", "ODI Runs", "T20I Runs", "Overall Average"]
    },

    12: {
        "title": "Home vs Away Performance",
        "difficulty": "intermediate",
        "description": "Analyze team performance in home vs away conditions", 
        "sql": """
        WITH team_match_location AS (
            SELECT 
                m.match_id,
                t1.team_id,
                t1.team_name,
                CASE 
                    WHEN t1.country = v.country THEN 'Home'
                    ELSE 'Away'
                END AS location,
                mr.winning_team_id
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
            LEFT JOIN match_results mr ON m.match_id = mr.match_id
            
            UNION ALL
            
            SELECT 
                m.match_id,
                t2.team_id,
                t2.team_name,
                CASE 
                    WHEN t2.country = v.country THEN 'Home'
                    ELSE 'Away'
                END AS location,
                mr.winning_team_id
            FROM matches m
            JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
            LEFT JOIN match_results mr ON m.match_id = mr.match_id
        )
        SELECT 
            team_name AS "Team Name",
            SUM(CASE WHEN location = 'Home' AND team_id = winning_team_id THEN 1 ELSE 0 END) AS "Home Wins",
            SUM(CASE WHEN location = 'Away' AND team_id = winning_team_id THEN 1 ELSE 0 END) AS "Away Wins",
            COUNT(CASE WHEN location = 'Home' THEN 1 END) AS "Home Matches",
            COUNT(CASE WHEN location = 'Away' THEN 1 END) AS "Away Matches"
        FROM team_match_location
        GROUP BY team_name
        ORDER BY (SUM(CASE WHEN location = 'Home' AND team_id = winning_team_id THEN 1 ELSE 0 END) + 
                  SUM(CASE WHEN location = 'Away' AND team_id = winning_team_id THEN 1 ELSE 0 END)) DESC;
        """,
        "expected_columns": ["Team Name", "Home Wins", "Away Wins", "Home Matches", "Away Matches"]
    },

    13: {
        "title": "High-Value Batting Partnerships",
        "difficulty": "intermediate",
        "description": "Identify partnerships with 100+ combined runs",
        "sql": """
        SELECT 
            p1.player_name AS "Batsman 1",
            p2.player_name AS "Batsman 2",
            (bp1.runs_scored + bp2.runs_scored) AS "Partnership Runs",
            CONCAT('Innings ', bp1.innings_number) AS "Innings",
            m.match_description AS "Match"
        FROM batting_performances bp1
        JOIN batting_performances bp2 ON bp1.match_id = bp2.match_id 
            AND bp1.innings_number = bp2.innings_number
            AND bp1.team_id = bp2.team_id
            AND bp2.batting_position = bp1.batting_position + 1
        JOIN players p1 ON bp1.player_id = p1.player_id
        JOIN players p2 ON bp2.player_id = p2.player_id
        JOIN matches m ON bp1.match_id = m.match_id
        WHERE (bp1.runs_scored + bp2.runs_scored) >= 100
        ORDER BY (bp1.runs_scored + bp2.runs_scored) DESC;
        """,
        "expected_columns": ["Batsman 1", "Batsman 2", "Partnership Runs", "Innings", "Match"]
    },

    14: {
        "title": "Venue-Specific Bowling Analysis",
        "difficulty": "intermediate",
        "description": "Bowling performance analysis at specific venues",
        "sql": """
        SELECT 
            p.player_name AS "Bowler Name",
            v.venue_name AS "Venue",
            ROUND(AVG(bowl.economy_rate), 2) AS "Average Economy",
            SUM(bowl.wickets_taken) AS "Total Wickets",
            COUNT(bowl.match_id) AS "Matches Played"
        FROM players p
        JOIN bowling_performances bowl ON p.player_id = bowl.player_id
        JOIN matches m ON bowl.match_id = m.match_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE bowl.overs_bowled >= 4.0
        GROUP BY p.player_id, p.player_name, v.venue_id, v.venue_name
        HAVING COUNT(bowl.match_id) >= 3
        ORDER BY ROUND(AVG(bowl.economy_rate), 2) ASC;
        """,
        "expected_columns": ["Bowler Name", "Venue", "Average Economy", "Total Wickets", "Matches Played"]
    },

    15: {
        "title": "Close Match Performance Analysis",
        "difficulty": "intermediate", 
        "description": "Player performance in closely contested matches",
        "sql": """
        WITH close_matches AS (
            SELECT DISTINCT m.match_id
            FROM matches m
            JOIN match_results mr ON m.match_id = mr.match_id
            WHERE (mr.victory_type = 'runs' AND mr.victory_margin < 50)
               OR (mr.victory_type = 'wickets' AND mr.victory_margin < 5)
        ),
        player_close_match_stats AS (
            SELECT 
                bp.player_id,
                bp.team_id,
                AVG(bp.runs_scored) as avg_runs,
                COUNT(bp.match_id) as close_matches_played,
                SUM(CASE WHEN bp.team_id = mr.winning_team_id THEN 1 ELSE 0 END) as wins_when_batted
            FROM batting_performances bp
            JOIN close_matches cm ON bp.match_id = cm.match_id
            JOIN match_results mr ON bp.match_id = mr.match_id
            GROUP BY bp.player_id, bp.team_id
        )
        SELECT 
            p.player_name AS "Player Name",
            ROUND(pcms.avg_runs, 2) AS "Average Runs in Close Matches",
            pcms.close_matches_played AS "Close Matches Played",
            pcms.wins_when_batted AS "Close Match Wins When Batted"
        FROM players p
        JOIN player_close_match_stats pcms ON p.player_id = pcms.player_id
        WHERE pcms.close_matches_played > 0
        ORDER BY pcms.avg_runs DESC;
        """,
        "expected_columns": ["Player Name", "Average Runs in Close Matches", "Close Matches Played", "Close Match Wins When Batted"]
    },

    16: {
        "title": "Performance Trends Over Years",
        "difficulty": "intermediate",
        "description": "Track batting performance changes since 2020",
        "sql": """
        SELECT 
            p.player_name AS "Player Name",
            EXTRACT(YEAR FROM m.match_date) AS "Year",
            ROUND(AVG(bp.runs_scored), 2) AS "Average Runs per Match",
            ROUND(AVG(bp.strike_rate), 2) AS "Average Strike Rate",
            COUNT(bp.match_id) AS "Matches Played"
        FROM players p
        JOIN batting_performances bp ON p.player_id = bp.player_id
        JOIN matches m ON bp.match_id = m.match_id
        WHERE m.match_date >= '2020-01-01'
        GROUP BY p.player_id, p.player_name, EXTRACT(YEAR FROM m.match_date)
        HAVING COUNT(bp.match_id) >= 5
        ORDER BY p.player_name, EXTRACT(YEAR FROM m.match_date) DESC;
        """,
        "expected_columns": ["Player Name", "Year", "Average Runs per Match", "Average Strike Rate", "Matches Played"]
    }
}

# Filter queries based on difficulty selection
def get_filtered_queries():
    if difficulty_filter == "Beginner (1-8)":
        return {k: v for k, v in ANALYTICS_QUERIES.items() if k <= 8}
    elif difficulty_filter == "Intermediate (9-16)":
        return {k: v for k, v in ANALYTICS_QUERIES.items() if k >= 9}
    else:
        return ANALYTICS_QUERIES

filtered_queries = get_filtered_queries()

# Display analytics queries
for query_num, query_info in filtered_queries.items():
    st.markdown('<div class="query-section">', unsafe_allow_html=True)
    
    # Header with difficulty badge
    difficulty_class = query_info["difficulty"]
    badge_text = difficulty_class.title()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Q{query_num}: {query_info['title']}")
    with col2:
        st.markdown(f'<span class="difficulty-badge {difficulty_class}">{badge_text}</span>', unsafe_allow_html=True)
    
    st.markdown(f"**Description:** {query_info['description']}")
    
    # Show/Hide SQL code
    with st.expander(f"📝 View SQL Code - Query {query_num}"):
        st.markdown(f'<div class="sql-code">{query_info["sql"]}</div>', unsafe_allow_html=True)
    
    # Execute query button
    if st.button(f"🚀 Execute Query {query_num}", key=f"exec_{query_num}", type="secondary"):
        with st.spinner(f"⏳ Executing Query {query_num}..."):
            result, exec_time = execute_analytics_query(query_info["sql"], query_info["title"])
            
            if result is not None:
                # Show summary
                st.markdown(f"""
                <div class="result-summary">
                    <strong>📊 Results Summary:</strong><br>
                    • Rows returned: {len(result)}<br>
                    • Columns: {len(result.columns)}<br>
                    • Execution time: {exec_time}ms
                </div>
                """, unsafe_allow_html=True)
                
                # Display interactive dataframe
                st.dataframe(
                    result, 
                    use_container_width=True,
                    hide_index=True,
                    height=min(400, (len(result) + 1) * 35)  # Dynamic height
                )
                
                # Download option
                csv = result.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download Query {query_num} Results as CSV",
                    data=csv,
                    file_name=f"cricket_analytics_query_{query_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

# Summary section in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("📈 **Query Statistics:**")
total_queries = len(ANALYTICS_QUERIES)
beginner_count = len([q for q in ANALYTICS_QUERIES.values() if q["difficulty"] == "beginner"])
intermediate_count = len([q for q in ANALYTICS_QUERIES.values() if q["difficulty"] == "intermediate"])

st.sidebar.metric("Total Queries", total_queries)
st.sidebar.metric("Beginner Level", beginner_count)
st.sidebar.metric("Intermediate Level", intermediate_count)

# Footer
st.markdown("---")
st.markdown("*📊 Advanced SQL analytics for comprehensive cricket data insights*")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")