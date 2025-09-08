import requests
from sqlalchemy import text
from utils.db_connection import get_connection

# 🔑 Replace with your API key
API_KEY = "afa80a6959msh437946c66a0f1f9p1ef4cejsn45b437dcf0e9"

url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
headers = {
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

def fetch_and_insert():
    conn = get_connection()
    if not conn:
        print("❌ DB connection failed.")
        return
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ API Error:", response.text)
        return
    
    data = response.json()

    # Loop over match types (League, Domestic, Women, etc.)
    for type_match in data.get("typeMatches", []):
        for series in type_match.get("seriesMatches", []):
            series_wrapper = series.get("seriesAdWrapper", {})
            for match in series_wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})
                venue_info = match_info.get("venueInfo", {})

                # Extract teams
                team1 = match_info.get("team1", {}).get("teamName", "")
                team2 = match_info.get("team2", {}).get("teamName", "")

                # Insert teams
                conn.execute(text("INSERT INTO teams (team_name) VALUES (:t) ON CONFLICT DO NOTHING"), {"t": team1})
                conn.execute(text("INSERT INTO teams (team_name) VALUES (:t) ON CONFLICT DO NOTHING"), {"t": team2})

                # Insert venue
                venue_name = venue_info.get("ground", "")
                city = venue_info.get("city", "")
                country = "Unknown"  # Cricbuzz doesn’t return directly
                capacity = None
                conn.execute(
                    text("INSERT INTO venues (venue_name, city, country, capacity) VALUES (:v, :c, :co, :cap) ON CONFLICT DO NOTHING"),
                    {"v": venue_name, "c": city, "co": country, "cap": capacity}
                )

                # Insert match
                match_desc = match_info.get("matchDesc", "")
                format_type = match_info.get("matchFormat", "")
                state = match_info.get("stateTitle", "")
                series_name = match_info.get("seriesName", "")

                conn.execute(
                    text("""
                        INSERT INTO matches (match_description, match_date, victory_type)
                        VALUES (:desc, CURRENT_DATE, :fmt)
                    """),
                    {"desc": f"{series_name} - {match_desc} ({state})", "fmt": format_type}
                )

                print(f"✅ Inserted match: {series_name} - {match_desc}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fetch_and_insert()
