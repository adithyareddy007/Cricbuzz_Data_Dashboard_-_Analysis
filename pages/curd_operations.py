import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_connection
import pandas as pd

st.set_page_config(page_title="CRUD Operations | Cricbuzz", layout="wide", page_icon="🛠️")

# Custom CSS
st.markdown("""
<style>
    .crud-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #007bff;
    }
    .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-msg {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    .delete-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛠️ CRUD Operations - Cricket Data Management")
st.markdown("*Complete data management for players, matches, teams, and venues*")

# --- Sidebar: Select Table ---
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: CRUD Operations")
st.sidebar.markdown("---")

table_choice = st.sidebar.selectbox(
    "Select Table", 
    ["Players", "Teams", "Venues", "Matches", "Match Scores"],
    help="Choose which data table to manage"
)

# Show table info
table_info = {
    "Players": "👨‍💼 Manage cricket players and their basic stats",
    "Teams": "🏏 Manage cricket teams",  
    "Venues": "🏟️ Manage cricket venues and stadiums",
    "Matches": "🎯 Manage match information",
    "Match Scores": "📊 Manage match scores and results"
}

st.sidebar.info(table_info[table_choice])

# Connect to DB
conn = get_connection()
if not conn:
    st.error("❌ Database connection failed. Please check your database configuration.")
    st.stop()

# Helper function to execute queries safely
def execute_query(query, params=None, fetch=False):
    try:
        if params:
            result = conn.execute(text(query), params)
        else:
            result = conn.execute(text(query))
        
        if fetch:
            return result.fetchall(), result.keys()
        else:
            conn.commit()
            return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)

# ---------------- PLAYERS CRUD ----------------
if table_choice == "Players":
    st.markdown('<div class="crud-section">', unsafe_allow_html=True)
    
    # CREATE
    st.subheader("➕ Add New Player")
    with st.form("create_player"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Player Name*", help="Full name of the player")
            country = st.text_input("Country", help="Player's country")
        with col2:
            matches = st.number_input("Total Matches", min_value=0, step=1, value=0)
            runs = st.number_input("Total Runs", min_value=0, step=1, value=0)
            wickets = st.number_input("Total Wickets", min_value=0, step=1, value=0)
        
        submitted = st.form_submit_button("Add Player", type="primary")
        if submitted:
            if not name.strip():
                st.error("❌ Player name is required!")
            else:
                success, error = execute_query(
                    """INSERT INTO players (name, country, matches, runs, wickets) 
                       VALUES (:name, :country, :matches, :runs, :wickets) 
                       ON CONFLICT (name) DO NOTHING""",
                    {"name": name.strip(), "country": country or None, "matches": matches, "runs": runs, "wickets": wickets}
                )
                if success:
                    st.success(f"✅ Player '{name}' added successfully!")
                else:
                    st.error(f"❌ Error adding player: {error}")

    # READ
    st.subheader("📖 Players List")
    players_data, headers = execute_query("SELECT * FROM players ORDER BY name", fetch=True)
    if players_data:
        df = pd.DataFrame(players_data, columns=headers)
        st.dataframe(df, use_container_width=True)
        st.info(f"📊 Total players: {len(df)}")
    else:
        st.warning("No players found in database.")

    # UPDATE
    st.subheader("✏️ Update Player")
    if players_data:
        player_names = [row[1] for row in players_data]  # name is second column
        selected_name = st.selectbox("Select Player to Update", player_names)
        
        # Get current player data
        current_player = next((row for row in players_data if row[1] == selected_name), None)
        if current_player:
            with st.form("update_player"):
                col1, col2 = st.columns(2)
                with col1:
                    new_country = st.text_input("Country", value=current_player[2] or "")
                    new_matches = st.number_input("Matches", min_value=0, step=1, value=current_player[3] or 0)
                with col2:
                    new_runs = st.number_input("Runs", min_value=0, step=1, value=current_player[4] or 0)
                    new_wickets = st.number_input("Wickets", min_value=0, step=1, value=current_player[5] or 0)
                
                submitted = st.form_submit_button("Update Player", type="primary")
                if submitted:
                    success, error = execute_query(
                        """UPDATE players SET country=:country, matches=:matches, runs=:runs, wickets=:wickets 
                           WHERE name=:name""",
                        {"country": new_country or None, "matches": new_matches, "runs": new_runs, 
                         "wickets": new_wickets, "name": selected_name}
                    )
                    if success:
                        st.success(f"✅ Player '{selected_name}' updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error updating player: {error}")

    # DELETE
    st.subheader("🗑️ Delete Player")
    if players_data:
        player_names = [row[1] for row in players_data]
        del_name = st.selectbox("Select Player to Delete", player_names, key="delete_player_select")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(f"🗑️ Delete", type="secondary"):
                st.session_state.confirm_delete_player = del_name
        
        if st.session_state.get('confirm_delete_player') == del_name:
            st.markdown(f'<div class="delete-warning">⚠️ Are you sure you want to delete player "{del_name}"? This action cannot be undone and will also delete all related statistics.</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", type="primary"):
                    success, error = execute_query("DELETE FROM players WHERE name=:name", {"name": del_name})
                    if success:
                        st.success(f"✅ Player '{del_name}' deleted successfully!")
                        if 'confirm_delete_player' in st.session_state:
                            del st.session_state.confirm_delete_player
                        st.rerun()
                    else:
                        st.error(f"❌ Error deleting player: {error}")
            
            with col2:
                if st.button("❌ Cancel"):
                    if 'confirm_delete_player' in st.session_state:
                        del st.session_state.confirm_delete_player
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- TEAMS CRUD ----------------
elif table_choice == "Teams":
    st.markdown('<div class="crud-section">', unsafe_allow_html=True)
    
    # CREATE
    st.subheader("➕ Add New Team")
    with st.form("create_team"):
        team_name = st.text_input("Team Name*", help="Official team name")
        submitted = st.form_submit_button("Add Team", type="primary")
        
        if submitted:
            if not team_name.strip():
                st.error("❌ Team name is required!")
            else:
                success, error = execute_query(
                    "INSERT INTO teams (team_name) VALUES (:name) ON CONFLICT (team_name) DO NOTHING",
                    {"name": team_name.strip()}
                )
                if success:
                    st.success(f"✅ Team '{team_name}' added successfully!")
                else:
                    st.error(f"❌ Error adding team: {error}")

    # READ
    st.subheader("📖 Teams List")
    teams_data, headers = execute_query("SELECT * FROM teams ORDER BY team_name", fetch=True)
    if teams_data:
        df = pd.DataFrame(teams_data, columns=headers)
        st.dataframe(df, use_container_width=True)
        st.info(f"📊 Total teams: {len(df)}")
    else:
        st.warning("No teams found in database.")

    # UPDATE
    st.subheader("✏️ Update Team")
    if teams_data:
        team_names = [row[1] for row in teams_data]
        selected_team = st.selectbox("Select Team to Update", team_names)
        
        with st.form("update_team"):
            new_name = st.text_input("New Team Name", value=selected_team)
            submitted = st.form_submit_button("Update Team", type="primary")
            
            if submitted:
                if not new_name.strip():
                    st.error("❌ Team name cannot be empty!")
                else:
                    success, error = execute_query(
                        "UPDATE teams SET team_name=:new_name WHERE team_name=:old_name",
                        {"new_name": new_name.strip(), "old_name": selected_team}
                    )
                    if success:
                        st.success(f"✅ Team updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error updating team: {error}")

    # DELETE
    st.subheader("🗑️ Delete Team")
    if teams_data:
        team_names = [row[1] for row in teams_data]
        del_team = st.selectbox("Select Team to Delete", team_names, key="delete_team_select")
        
        if st.button(f"🗑️ Delete Team", type="secondary"):
            st.session_state.confirm_delete_team = del_team
        
        if st.session_state.get('confirm_delete_team') == del_team:
            st.markdown(f'<div class="delete-warning">⚠️ Are you sure you want to delete team "{del_team}"? This will also affect related matches and scores.</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Delete", type="primary"):
                    success, error = execute_query("DELETE FROM teams WHERE team_name=:name", {"name": del_team})
                    if success:
                        st.success(f"✅ Team '{del_team}' deleted successfully!")
                        if 'confirm_delete_team' in st.session_state:
                            del st.session_state.confirm_delete_team
                        st.rerun()
                    else:
                        st.error(f"❌ Error deleting team: {error}")
            
            with col2:
                if st.button("❌ Cancel Delete"):
                    if 'confirm_delete_team' in st.session_state:
                        del st.session_state.confirm_delete_team
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- VENUES CRUD ----------------
elif table_choice == "Venues":
    st.markdown('<div class="crud-section">', unsafe_allow_html=True)
    
    # CREATE
    st.subheader("➕ Add New Venue")
    with st.form("create_venue"):
        col1, col2 = st.columns(2)
        with col1:
            venue_name = st.text_input("Venue Name*", help="Stadium or ground name")
            city = st.text_input("City", help="City where venue is located")
        with col2:
            country = st.text_input("Country", help="Country where venue is located")
            capacity = st.number_input("Capacity", min_value=0, step=1000, help="Seating capacity")
        
        submitted = st.form_submit_button("Add Venue", type="primary")
        if submitted:
            if not venue_name.strip():
                st.error("❌ Venue name is required!")
            else:
                success, error = execute_query(
                    """INSERT INTO venues (venue_name, city, country, capacity) 
                       VALUES (:name, :city, :country, :capacity) 
                       ON CONFLICT (venue_name) DO NOTHING""",
                    {"name": venue_name.strip(), "city": city or None, "country": country or None, 
                     "capacity": capacity if capacity > 0 else None}
                )
                if success:
                    st.success(f"✅ Venue '{venue_name}' added successfully!")
                else:
                    st.error(f"❌ Error adding venue: {error}")

    # READ
    st.subheader("📖 Venues List")
    venues_data, headers = execute_query("SELECT * FROM venues ORDER BY venue_name", fetch=True)
    if venues_data:
        df = pd.DataFrame(venues_data, columns=headers)
        st.dataframe(df, use_container_width=True)
        st.info(f"📊 Total venues: {len(df)}")
    else:
        st.warning("No venues found in database.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MATCHES CRUD ----------------
elif table_choice == "Matches":
    st.markdown('<div class="crud-section">', unsafe_allow_html=True)
    
    # First get available venues for dropdown
    venues_data, _ = execute_query("SELECT venue_id, venue_name FROM venues ORDER BY venue_name", fetch=True)
    venue_options = {f"{row[1]}": row[0] for row in venues_data} if venues_data else {}
    
    # CREATE
    st.subheader("➕ Add New Match")
    with st.form("create_match"):
        col1, col2 = st.columns(2)
        with col1:
            match_id = st.number_input("Match ID*", min_value=1, help="Unique match identifier")
            match_desc = st.text_input("Match Description*", help="e.g., 'India vs Australia, 1st Test'")
        with col2:
            match_date = st.date_input("Match Date", help="Date of the match")
            victory_type = st.selectbox("Match Type", ["Test", "ODI", "T20"], help="Format of cricket")
            
        venue_name = st.selectbox("Venue", ["Select Venue"] + list(venue_options.keys()), help="Match venue")
        
        submitted = st.form_submit_button("Add Match", type="primary")
        if submitted:
            if not match_desc.strip():
                st.error("❌ Match description is required!")
            elif venue_name == "Select Venue":
                venue_id = None
            else:
                venue_id = venue_options.get(venue_name)
            
            if match_desc.strip():
                success, error = execute_query(
                    """INSERT INTO matches (match_id, match_description, match_date, victory_type, venue_id) 
                       VALUES (:id, :desc, :date, :type, :venue) 
                       ON CONFLICT (match_id) DO NOTHING""",
                    {"id": match_id, "desc": match_desc.strip(), "date": match_date, 
                     "type": victory_type, "venue": venue_id}
                )
                if success:
                    st.success(f"✅ Match added successfully!")
                else:
                    st.error(f"❌ Error adding match: {error}")

    # READ
    st.subheader("📖 Matches List")
    matches_data, headers = execute_query("""
        SELECT m.match_id, m.match_description, m.match_date, m.victory_type, v.venue_name 
        FROM matches m 
        LEFT JOIN venues v ON m.venue_id = v.venue_id 
        ORDER BY m.match_date DESC
    """, fetch=True)
    
    if matches_data:
        df = pd.DataFrame(matches_data, columns=["Match ID", "Description", "Date", "Type", "Venue"])
        st.dataframe(df, use_container_width=True)
        st.info(f"📊 Total matches: {len(df)}")
    else:
        st.warning("No matches found in database.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MATCH SCORES CRUD ----------------
elif table_choice == "Match Scores":
    st.markdown('<div class="crud-section">', unsafe_allow_html=True)
    
    # Get available matches and teams for dropdowns
    matches_data, _ = execute_query("SELECT match_id, match_description FROM matches ORDER BY match_date DESC", fetch=True)
    match_options = {f"{row[1]} (ID: {row[0]})": row[0] for row in matches_data} if matches_data else {}
    
    teams_data, _ = execute_query("SELECT team_id, team_name FROM teams ORDER BY team_name", fetch=True)
    team_options = {row[1]: row[0] for row in teams_data} if teams_data else {}

    # CREATE/UPDATE
    st.subheader("➕ Add/Update Match Score")
    with st.form("create_score"):
        col1, col2 = st.columns(2)
        with col1:
            match_choice = st.selectbox("Select Match", ["Select Match"] + list(match_options.keys()))
            team_choice = st.selectbox("Select Team", ["Select Team"] + list(team_options.keys()))
        with col2:
            runs = st.number_input("Runs", min_value=0, step=1)
            wickets = st.number_input("Wickets", min_value=0, max_value=10, step=1)
            overs = st.number_input("Overs", min_value=0.0, step=0.1, format="%.1f")
        
        submitted = st.form_submit_button("Add/Update Score", type="primary")
        if submitted:
            if match_choice == "Select Match" or team_choice == "Select Team":
                st.error("❌ Please select both match and team!")
            else:
                match_id = match_options[match_choice]
                team_id = team_options[team_choice]
                
                success, error = execute_query(
                    """INSERT INTO match_scores (match_id, team_id, runs, wickets, overs) 
                       VALUES (:match_id, :team_id, :runs, :wickets, :overs)
                       ON CONFLICT (match_id, team_id) DO UPDATE 
                       SET runs = EXCLUDED.runs, wickets = EXCLUDED.wickets, overs = EXCLUDED.overs""",
                    {"match_id": match_id, "team_id": team_id, "runs": runs, "wickets": wickets, "overs": overs}
                )
                if success:
                    st.success(f"✅ Score updated successfully!")
                else:
                    st.error(f"❌ Error updating score: {error}")

    # READ
    st.subheader("📖 Match Scores")
    scores_data, headers = execute_query("""
        SELECT m.match_description, t.team_name, ms.runs, ms.wickets, ms.overs, m.match_date
        FROM match_scores ms
        JOIN matches m ON ms.match_id = m.match_id
        JOIN teams t ON ms.team_id = t.team_id
        ORDER BY m.match_date DESC, t.team_name
    """, fetch=True)
    
    if scores_data:
        df = pd.DataFrame(scores_data, columns=["Match", "Team", "Runs", "Wickets", "Overs", "Date"])
        st.dataframe(df, use_container_width=True)
        st.info(f"📊 Total score records: {len(df)}")
    else:
        st.warning("No match scores found in database.")

    st.markdown('</div>', unsafe_allow_html=True)

# Close database connection
conn.close()

# Footer
st.markdown("---")
st.markdown("*🔧 Complete CRUD operations for cricket database management*")