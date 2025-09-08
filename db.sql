-- ================================
-- 🏏 Cricbuzz LiveStats Full Schema
-- ================================

-- Drop tables in correct order to handle dependencies
--DROP TABLE IF EXISTS batting_stats CASCADE;
--DROP TABLE IF EXISTS bowling_stats CASCADE;
--DROP TABLE IF EXISTS match_scores CASCADE;
--DROP TABLE IF EXISTS matches CASCADE;
--DROP TABLE IF EXISTS players CASCADE;
--DROP TABLE IF EXISTS venues CASCADE;
--DROP TABLE IF EXISTS teams CASCADE;

-- -------------------
-- Teams
-- -------------------
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_name TEXT UNIQUE NOT NULL
);

-- -------------------
-- Venues
-- -------------------
CREATE TABLE venues (
    venue_id SERIAL PRIMARY KEY,
    venue_name TEXT UNIQUE NOT NULL,
    city TEXT,
    country TEXT,
    capacity INT
);

-- -------------------
-- Matches
-- -------------------
CREATE TABLE matches (
    match_id BIGINT PRIMARY KEY,
    match_description TEXT,
    match_date DATE,
    victory_type TEXT CHECK (victory_type IN ('Test', 'ODI', 'T20')),
    venue_id INT REFERENCES venues(venue_id) ON DELETE SET NULL
);

-- -------------------
-- Match Scores
-- -------------------
CREATE TABLE match_scores (
    score_id SERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(match_id) ON DELETE CASCADE,
    team_id INT REFERENCES teams(team_id) ON DELETE CASCADE,
    runs INT,
    wickets INT,
    overs NUMERIC(5,1),
    UNIQUE (match_id, team_id)
);

-- -------------------
-- Players
-- -------------------
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    country TEXT,
    matches INT DEFAULT 0,
    runs INT DEFAULT 0,
    wickets INT DEFAULT 0
);

-- -------------------
-- Batting Stats
-- -------------------
CREATE TABLE batting_stats (
    stat_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id) ON DELETE CASCADE,
    format TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    value INT NOT NULL,
    matches INT DEFAULT 0,
    UNIQUE (player_id, format, stat_type)
);

-- -------------------
-- Bowling Stats
-- -------------------
CREATE TABLE bowling_stats (
    stat_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id) ON DELETE CASCADE,
    format TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    value INT NOT NULL,
    matches INT DEFAULT 0,
    UNIQUE (player_id, format, stat_type)
);
