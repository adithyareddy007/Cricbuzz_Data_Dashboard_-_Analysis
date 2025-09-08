import requests
import os
from dotenv import load_dotenv
from sqlalchemy import text
from utils.db_connection import get_connection

# Load environment variables
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")

url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
headers = {
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

def etl_load():
    conn = get_connection()
    if not conn:
        print("❌ DB connection failed.")
        return

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ API Error:", response.text)
        return

    data = response.json()

    for type_match in data.get("typeMatches", []):
        for series in type_match.get("seriesMatches", []):
            series_wrapper = series.get("seriesAdWrapper", {})
            for match in series_wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})
                venue_info = match_info.get("venueInfo", {})

                # ---------------- Teams ----------------
                team_ids = {}
                for team_key in ["team1", "team2"]:
                    team_name = match_info.get(team_key, {}).get("teamName", "")
                    if not team_name:
                        continue
                    try:
                        query = """
                        INSERT INTO teams (team_name)
                        VALUES (:team_name)
                        ON CONFLICT (team_name) DO NOTHING
                        RETURNING team_id
                        """
                        res = conn.execute(text(query), {"team_name": team_name}).fetchone()
                        if res:
                            team_ids[team_key] = res[0]
                        else:
                            query2 = "SELECT team_id FROM teams WHERE team_name=:team_name"
                            team_ids[team_key] = conn.execute(text(query2), {"team_name": team_name}).fetchone()[0]
                    except Exception as e:
                        print(f"❌ Error inserting team {team_name}: {e}")
                        conn.rollback()

                # ---------------- Venue ----------------
                venue_name = venue_info.get("ground", "")
                city = venue_info.get("city", "")
                country = "Unknown"
                capacity = None
                venue_id = None

                if venue_name:
                    try:
                        query = """
                        INSERT INTO venues (venue_name, city, country, capacity)
                        VALUES (:venue_name, :city, :country, :capacity)
                        ON CONFLICT (venue_name) DO NOTHING
                        RETURNING venue_id
                        """
                        res = conn.execute(
                            text(query),
                            {"venue_name": venue_name, "city": city, "country": country, "capacity": capacity},
                        ).fetchone()
                        if res:
                            venue_id = res[0]
                        else:
                            query2 = "SELECT venue_id FROM venues WHERE venue_name=:venue_name"
                            venue_id = conn.execute(text(query2), {"venue_name": venue_name}).fetchone()[0]
                    except Exception as e:
                        print(f"❌ Error inserting venue {venue_name}: {e}")
                        conn.rollback()

                # ---------------- Match ----------------
                match_id = match_info.get("matchId", 0)
                match_desc = match_info.get("matchDesc", "")
                series_name = match_info.get("seriesName", "")
                match_date = match_info.get("startDate", None)  # or use CURRENT_DATE

                if match_desc:
                    try:
                        query = """
                        INSERT INTO matches (match_id, match_description, match_date, venue_id)
                        VALUES (:mid, :desc, CURRENT_DATE, :vid)
                        ON CONFLICT (match_id) DO NOTHING
                        """
                        conn.execute(
                            text(query),
                            {"mid": match_id, "desc": f"{series_name} - {match_desc}", "vid": venue_id},
                        )
                        print(f"✅ Inserted match: {series_name} - {match_desc}")
                    except Exception as e:
                        print(f"❌ Error inserting match {match_id}: {e}")
                        conn.rollback()

                # ---------------- Scores ----------------
                match_score = match.get("matchScore", {})
                for team_key, team_id in [("team1Score", team_ids.get("team1")), ("team2Score", team_ids.get("team2"))]:
                    if team_key in match_score and team_id:
                        innings = match_score[team_key].get("inngs1", {})
                        runs = innings.get("runs")
                        wickets = innings.get("wickets", 0)
                        overs = innings.get("overs", 0.0)

                        if runs is not None:
                            try:
                                query = """
                                INSERT INTO match_scores (match_id, team_id, runs, wickets, overs)
                                VALUES (:mid, :tid, :runs, :wickets, :overs)
                                ON CONFLICT (match_id, team_id) DO UPDATE
                                SET runs = EXCLUDED.runs,
                                    wickets = EXCLUDED.wickets,
                                    overs = EXCLUDED.overs
                                """
                                conn.execute(
                                    text(query),
                                    {"mid": match_id, "tid": team_id, "runs": runs, "wickets": wickets, "overs": overs},
                                )
                                print(f"   ➡️ Score updated: {runs}/{wickets} in {overs} overs")
                            except Exception as e:
                                print(f"❌ Error updating score for match {match_id}: {e}")
                                conn.rollback()

    conn.commit()
    conn.close()
    print("🎉 ETL completed successfully.")

if __name__ == "__main__":
    etl_load()
