import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_connection
import pandas as pd

st.set_page_config(page_title="CRUD Operations | Cricbuzz", layout="wide")
st.title("🛠️ CRUD Operations - Player & Match Stats")

# --- Sidebar: Select Table ---
table_choice = st.sidebar.selectbox("Select Table", ["Players", "Matches"])

# Connect to DB
conn = get_connection()
if not conn:
    st.error("❌ Database connection failed.")
else:

    # ---------------- CREATE ----------------
    st.header("➕ Create Record")
    with st.expander("Add New Record"):

        if table_choice == "Players":
            with st.form("create_player"):
                name = st.text_input("Player Name")
                matches = st.number_input("Matches", min_value=0, step=1)
                runs = st.number_input("Runs", min_value=0, step=1)
                wickets = st.number_input("Wickets", min_value=0, step=1)
                submitted = st.form_submit_button("Add Player")
                if submitted:
                    try:
                        conn.execute(
                            text(
                                "INSERT INTO players (name, matches, runs, wickets) "
                                "VALUES (:n, :m, :r, :w) "
                                "ON CONFLICT (name) DO NOTHING"
                            ),
                            {"n": name, "m": matches, "r": runs, "w": wickets}
                        )
                        conn.commit()
                        st.success(f"Player {name} added successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif table_choice == "Matches":
            with st.form("create_match"):
                match_id = st.text_input("Match ID")
                team1 = st.text_input("Team 1")
                team2 = st.text_input("Team 2")
                format_type = st.selectbox("Format", ["test", "odi", "t20"])
                winner = st.text_input("Winner")
                submitted = st.form_submit_button("Add Match")
                if submitted:
                    try:
                        conn.execute(
                            text(
                                "INSERT INTO matches (match_id, team1, team2, format_type, winner) "
                                "VALUES (:id, :t1, :t2, :fmt, :w) "
                                "ON CONFLICT (match_id) DO NOTHING"
                            ),
                            {"id": match_id, "t1": team1, "t2": team2, "fmt": format_type, "w": winner}
                        )
                        conn.commit()
                        st.success(f"Match {match_id} added successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ---------------- READ ----------------
    st.header("📖 Read Records")
    if table_choice == "Players":
        df = pd.read_sql("SELECT * FROM players ORDER BY name", conn)
        st.dataframe(df)
    elif table_choice == "Matches":
        df = pd.read_sql("SELECT * FROM matches ORDER BY match_id", conn)
        st.dataframe(df)

    # ---------------- UPDATE ----------------
    st.header("✏️ Update Record")
    with st.expander("Update Record"):
        if table_choice == "Players":
            names = pd.read_sql("SELECT name FROM players", conn)["name"].tolist()
            selected_name = st.selectbox("Select Player to Update", names)
            with st.form("update_player"):
                new_matches = st.number_input("Matches", min_value=0, step=1)
                new_runs = st.number_input("Runs", min_value=0, step=1)
                new_wickets = st.number_input("Wickets", min_value=0, step=1)
                submitted = st.form_submit_button("Update Player")
                if submitted:
                    try:
                        conn.execute(
                            text(
                                "UPDATE players SET matches=:m, runs=:r, wickets=:w WHERE name=:n"
                            ),
                            {"m": new_matches, "r": new_runs, "w": new_wickets, "n": selected_name}
                        )
                        conn.commit()
                        st.success(f"Player {selected_name} updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif table_choice == "Matches":
            match_ids = pd.read_sql("SELECT match_id FROM matches", conn)["match_id"].tolist()
            selected_id = st.selectbox("Select Match to Update", match_ids)
            with st.form("update_match"):
                new_team1 = st.text_input("Team 1")
                new_team2 = st.text_input("Team 2")
                new_format = st.selectbox("Format", ["test", "odi", "t20"])
                new_winner = st.text_input("Winner")
                submitted = st.form_submit_button("Update Match")
                if submitted:
                    try:
                        conn.execute(
                            text(
                                "UPDATE matches SET team1=:t1, team2=:t2, format_type=:fmt, winner=:w WHERE match_id=:id"
                            ),
                            {"t1": new_team1, "t2": new_team2, "fmt": new_format, "w": new_winner, "id": selected_id}
                        )
                        conn.commit()
                        st.success(f"Match {selected_id} updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ---------------- DELETE ----------------
    st.header("🗑️ Delete Record")
    with st.expander("Delete Record"):
        if table_choice == "Players":
            names = pd.read_sql("SELECT name FROM players", conn)["name"].tolist()
            del_name = st.selectbox("Select Player to Delete", names)
            if st.button(f"Delete Player {del_name}"):
                try:
                    conn.execute(text("DELETE FROM players WHERE name=:n"), {"n": del_name})
                    conn.commit()
                    st.success(f"Player {del_name} deleted successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif table_choice == "Matches":
            match_ids = pd.read_sql("SELECT match_id FROM matches", conn)["match_id"].tolist()
            del_id = st.selectbox("Select Match to Delete", match_ids)
            if st.button(f"Delete Match {del_id}"):
                try:
                    conn.execute(text("DELETE FROM matches WHERE match_id=:id"), {"id": del_id})
                    conn.commit()
                    st.success(f"Match {del_id} deleted successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    conn.close()
