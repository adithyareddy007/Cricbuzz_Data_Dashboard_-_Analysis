-- Question 1: Find all players who represent India
SELECT 
    player_name AS "Full Name",
    playing_role AS "Playing Role",
    batting_style AS "Batting Style",
    bowling_style AS "Bowling Style"
FROM players 
WHERE country = 'India'
ORDER BY player_name;

-- Question 2: Show all cricket matches played in the last 30 days
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

-- Question 3: Top 10 highest run scorers in ODI cricket
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

-- Question 4: Venues with capacity > 50,000
SELECT 
    venue_name AS "Venue Name",
    city AS "City",
    country AS "Country",
    capacity AS "Capacity"
FROM venues 
WHERE capacity > 50000
ORDER BY capacity DESC;

-- Question 5: Count wins for each team
SELECT 
    t.team_name AS "Team Name",
    COUNT(mr.winning_team_id) AS "Total Wins"
FROM teams t
LEFT JOIN match_results mr ON t.team_id = mr.winning_team_id
GROUP BY t.team_id, t.team_name
ORDER BY COUNT(mr.winning_team_id) DESC;

-- Question 6: Count players by playing role
SELECT 
    playing_role AS "Playing Role",
    COUNT(*) AS "Number of Players"
FROM players 
WHERE playing_role IS NOT NULL
GROUP BY playing_role
ORDER BY COUNT(*) DESC;

-- Question 7: Highest individual batting score in each format
SELECT 
    m.match_type AS "Format",
    MAX(bp.runs_scored) AS "Highest Score"
FROM batting_performances bp
JOIN matches m ON bp.match_id = m.match_id
GROUP BY m.match_type
ORDER BY MAX(bp.runs_scored) DESC;

-- Question 8: Cricket series that started in 2024
SELECT 
    series_name AS "Series Name",
    host_country AS "Host Country",
    match_type AS "Match Type",
    start_date AS "Start Date",
    total_matches AS "Total Matches"
FROM series 
WHERE EXTRACT(YEAR FROM start_date) = 2024
ORDER BY start_date;



-- Question 9: All-rounders with 1000+ runs AND 50+ wickets
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

-- Question 10: Last 20 completed matches with details
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

-- Question 11: Player performance across different formats
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

-- Question 12: Team performance at home vs away
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

-- Question 13: Batting partnerships with 100+ combined runs
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

-- Question 14: Bowling performance at venues (3+ matches, 4+ overs each)
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

-- Question 15: Players performance in close matches
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

-- Question 16: Player batting performance changes over years (since 2020)
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