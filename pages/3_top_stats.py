import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Page Config
st.set_page_config(page_title="Top Stats | Cricbuzz LiveStats", layout="wide")

# Sidebar
st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.markdown("📌 Page: Top Stats")

st.title("📊 Top Player Stats")

# DB connection
def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="postgres",
            password="adi1234",
            port="5432"
        )
        return conn
    except Exception as e:
        st.error(f"❌ DB Connection failed: {e}")
        return None

# Load API key
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")

if not API_KEY:
    st.error("❌ API key not found. Please set RAPIDAPI_KEY in your .env file.")
else:
    headers = {
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
    }

    # --- Fetch all stat types ---
    stats_url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats"
    stats_resp = requests.get(stats_url, headers=headers)

    if stats_resp.status_code == 200:
        stats_data = stats_resp.json().get("statsTypesList", [])
        stat_types = []
        for category in stats_data:
            for t in category["types"]:
                stat_types.append({
                    "value": t["value"],
                    "label": t["header"],
                    "category": t["category"]
                })

        # Step 1: Choose category
        category_choice = st.radio("📌 Choose Category", ["Batting", "Bowling"])

        # Step 2: Filter stat types by category
        filtered_stats = [t for t in stat_types if category_choice.lower() in t["category"].lower()]

        # Step 3: Format dropdown
        format_choice = st.selectbox("📌 Select Format", ["test", "odi", "t20"])
        stat_choice = st.selectbox(
            "📊 Select Stat Type",
            [f"{t['label']} ({t['category']})" for t in filtered_stats]
        )

        stat_value = next(
            (t["value"] for t in filtered_stats if f"{t['label']} ({t['category']})" == stat_choice),
            "mostRuns"
        )

        # --- Fetch leaderboard ---
        top_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0?statsType={stat_value}"
        resp = requests.get(top_url, headers=headers, params={"formatType": format_choice})

        if resp.status_code == 200:
            data = resp.json()
            headers_list = data.get("headers", [])
            players = data.get("values", [])

            if players:
                values_list = [p["values"] for p in players]

                # Fix header/value mismatch
                if len(headers_list) < len(values_list[0]):
                    headers_list += [f"Extra_{i}" for i in range(len(headers_list), len(values_list[0]))]

                df = pd.DataFrame(values_list, columns=headers_list)
                st.subheader(f"🏏 {stat_choice} - {format_choice.upper()}")
                st.dataframe(df.head(10), use_container_width=True)

                # --- Save to Database ---
                conn = get_connection()
                if conn:
                    cur = conn.cursor()

                    for p in players[:10]:  # Save top 10
                        player_name = p["values"][0]   # first column = Player name
                        matches = None
                        value = None

                        # Try to map columns
                        for idx, col in enumerate(headers_list):
                            if "Mat" in col:
                                matches = p["values"][idx]
                            if idx > 0 and col not in ["Player"]:
                                try:
                                    value = int(p["values"][idx])
                                except:
                                    continue

                        # Insert into players table
                        cur.execute(
                            """
                            INSERT INTO players (name, matches)
                            VALUES (%s, COALESCE(%s,0))
                            ON CONFLICT (name) DO UPDATE SET matches = COALESCE(EXCLUDED.matches, players.matches)
                            """,
                            (player_name, matches)
                        )

                        # Get player_id
                        cur.execute("SELECT player_id FROM players WHERE name=%s", (player_name,))
                        result = cur.fetchone()
                        if result:
                            player_id = result[0]

                            if category_choice == "Batting":
                                cur.execute(
                                    """
                                    INSERT INTO batting_stats (player_id, format, stat_type, value, matches)
                                    VALUES (%s, %s, %s, %s, COALESCE(%s,0))
                                    ON CONFLICT (player_id, format, stat_type) DO UPDATE
                                    SET value = EXCLUDED.value, matches = EXCLUDED.matches
                                    """,
                                    (player_id, format_choice, stat_value, value, matches)
                                )
                            else:
                                cur.execute(
                                    """
                                    INSERT INTO bowling_stats (player_id, format, stat_type, value, matches)
                                    VALUES (%s, %s, %s, %s, COALESCE(%s,0))
                                    ON CONFLICT (player_id, format, stat_type) DO UPDATE
                                    SET value = EXCLUDED.value, matches = EXCLUDED.matches
                                    """,
                                    (player_id, format_choice, stat_value, value, matches)
                                )

                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("✅ Stats saved to database")
            else:
                st.warning("No data available for this stat.")
        else:
            st.error(f"API Error {resp.status_code}: {resp.text}")
    else:
        st.error(f"API Error: {stats_resp.status_code} - {stats_resp.text}")
