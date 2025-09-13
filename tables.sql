-- Teams table
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(100) NOT NULL,
    team_type VARCHAR(20) DEFAULT 'International', -- International, Domestic, etc.
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Venues table
CREATE TABLE venues (
    venue_id SERIAL PRIMARY KEY,
    venue_name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    capacity INTEGER,
    established_year INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players table
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(200) NOT NULL,
    country VARCHAR(100) NOT NULL,
    playing_role VARCHAR(50), -- Batsman, Bowler, All-rounder, Wicket-keeper
    batting_style VARCHAR(50), -- Right-handed, Left-handed
    bowling_style VARCHAR(100), -- Right-arm fast, Left-arm spin, etc.
    date_of_birth DATE,
    debut_date DATE,
    career_runs INTEGER DEFAULT 0,
    career_wickets INTEGER DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Series table
CREATE TABLE series (
    series_id SERIAL PRIMARY KEY,
    series_name VARCHAR(200) NOT NULL,
    host_country VARCHAR(100) NOT NULL,
    match_type VARCHAR(20) NOT NULL, -- Test, ODI, T20I
    start_date DATE NOT NULL,
    end_date DATE,
    total_matches INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Scheduled', -- Scheduled, Ongoing, Completed
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matches table
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    series_id INTEGER REFERENCES series(series_id),
    match_description VARCHAR(300) NOT NULL,
    team1_id INTEGER REFERENCES teams(team_id) NOT NULL,
    team2_id INTEGER REFERENCES teams(team_id) NOT NULL,
    venue_id INTEGER REFERENCES venues(venue_id),
    match_date DATE NOT NULL,
    match_type VARCHAR(20) NOT NULL, -- Test, ODI, T20I
    status VARCHAR(20) DEFAULT 'Scheduled', -- Scheduled, Ongoing, Completed
    toss_winner INTEGER REFERENCES teams(team_id),
    toss_decision VARCHAR(10), -- Bat, Bowl
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Match Results table
CREATE TABLE match_results (
    result_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    winning_team_id INTEGER REFERENCES teams(team_id),
    victory_margin INTEGER, -- runs or wickets
    victory_type VARCHAR(10), -- runs, wickets, tie, no result
    man_of_the_match INTEGER REFERENCES players(player_id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Batting Performances table
CREATE TABLE batting_performances (
    performance_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    player_id INTEGER REFERENCES players(player_id) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    innings_number INTEGER NOT NULL, -- 1 or 2
    batting_position INTEGER NOT NULL, -- 1-11
    runs_scored INTEGER DEFAULT 0,
    balls_faced INTEGER DEFAULT 0,
    fours INTEGER DEFAULT 0,
    sixes INTEGER DEFAULT 0,
    strike_rate DECIMAL(5,2) DEFAULT 0,
    dismissal_type VARCHAR(50), -- bowled, caught, lbw, etc.
    bowler_id INTEGER REFERENCES players(player_id), -- who got the wicket
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bowling Performances table
CREATE TABLE bowling_performances (
    performance_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
    player_id INTEGER REFERENCES players(player_id) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
    innings_number INTEGER NOT NULL, -- 1 or 2
    overs_bowled DECIMAL(3,1) DEFAULT 0,
    maidens INTEGER DEFAULT 0,
    runs_conceded INTEGER DEFAULT 0,
    wickets_taken INTEGER DEFAULT 0,
    economy_rate DECIMAL(4,2) DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_type ON matches(match_type);
CREATE INDEX idx_batting_player ON batting_performances(player_id);
CREATE INDEX idx_batting_match ON batting_performances(match_id);
CREATE INDEX idx_bowling_player ON bowling_performances(player_id);
CREATE INDEX idx_bowling_match ON bowling_performances(match_id);
CREATE INDEX idx_players_country ON players(country);
CREATE INDEX idx_players_role ON players(playing_role);
CREATE INDEX idx_venues_country ON venues(country);
CREATE INDEX idx_series_start_date ON series(start_date);

-- Insert sample data for testing

-- Insert Teams
INSERT INTO teams (team_name, country) VALUES
('India', 'India'),
('Australia', 'Australia'),
('England', 'England'),
('Pakistan', 'Pakistan'),
('South Africa', 'South Africa'),
('New Zealand', 'New Zealand'),
('Sri Lanka', 'Sri Lanka'),
('Bangladesh', 'Bangladesh'),
('West Indies', 'West Indies'),
('Afghanistan', 'Afghanistan');

-- Insert Venues
INSERT INTO venues (venue_name, city, country, capacity) VALUES
('Wankhede Stadium', 'Mumbai', 'India', 33108),
('Eden Gardens', 'Kolkata', 'India', 66000),
('Lords Cricket Ground', 'London', 'England', 31100),
('Melbourne Cricket Ground', 'Melbourne', 'Australia', 100024),
('The Oval', 'London', 'England', 25500),
('Narendra Modi Stadium', 'Ahmedabad', 'India', 132000),
('Sydney Cricket Ground', 'Sydney', 'Australia', 48000),
('Old Trafford', 'Manchester', 'England', 26000),
('Adelaide Oval', 'Adelaide', 'Australia', 53583),
('Dubai International Stadium', 'Dubai', 'UAE', 25000);

-- Insert Players
INSERT INTO players (player_name, country, playing_role, batting_style, bowling_style, career_runs, career_wickets) VALUES
('Virat Kohli', 'India', 'Batsman', 'Right-handed', NULL, 12169, 4),
('Rohit Sharma', 'India', 'Batsman', 'Right-handed', 'Right-arm off-break', 9205, 8),
('Jasprit Bumrah', 'India', 'Bowler', 'Right-handed', 'Right-arm fast', 89, 121),
('Ravindra Jadeja', 'India', 'All-rounder', 'Left-handed', 'Left-arm orthodox spin', 2756, 220),
('MS Dhoni', 'India', 'Wicket-keeper', 'Right-handed', 'Right-arm medium', 10773, 1),
('Steve Smith', 'Australia', 'Batsman', 'Right-handed', 'Right-arm leg-break', 8647, 17),
('Pat Cummins', 'Australia', 'Bowler', 'Right-handed', 'Right-arm fast', 845, 188),
('Ben Stokes', 'England', 'All-rounder', 'Left-handed', 'Right-arm fast-medium', 4956, 171),
('Joe Root', 'England', 'Batsman', 'Right-handed', 'Right-arm off-break', 9406, 27),
('Babar Azam', 'Pakistan', 'Batsman', 'Right-handed', 'Right-arm off-break', 4442, 0),
('Kane Williamson', 'New Zealand', 'Batsman', 'Right-handed', 'Right-arm off-break', 6173, 4),
('Trent Boult', 'New Zealand', 'Bowler', 'Left-handed', 'Left-arm fast-medium', 212, 169),
('Shakib Al Hasan', 'Bangladesh', 'All-rounder', 'Left-handed', 'Left-arm orthodox spin', 4114, 122),
('Quinton de Kock', 'South Africa', 'Wicket-keeper', 'Left-handed', NULL, 5422, 0),
('Kagiso Rabada', 'South Africa', 'Bowler', 'Right-handed', 'Right-arm fast', 298, 138);

-- Insert Series
INSERT INTO series (series_name, host_country, match_type, start_date, end_date, total_matches, status) VALUES
('India vs Australia Border-Gavaskar Trophy 2024', 'Australia', 'Test', '2024-01-15', '2024-02-15', 4, 'Completed'),
('ICC Cricket World Cup 2023', 'India', 'ODI', '2023-10-05', '2023-11-19', 48, 'Completed'),
('England vs Pakistan T20I Series 2024', 'England', 'T20I', '2024-05-22', '2024-05-30', 4, 'Completed'),
('India vs New Zealand Test Series 2024', 'India', 'Test', '2024-10-16', '2024-11-05', 3, 'Completed'),
('Australia vs South Africa ODI Series 2024', 'Australia', 'ODI', '2024-08-30', '2024-09-11', 3, 'Completed');

-- Insert Matches (last 30 days and some older matches)
INSERT INTO matches (series_id, match_description, team1_id, team2_id, venue_id, match_date, match_type, status) VALUES
(4, 'India vs New Zealand, 3rd Test', 1, 6, 2, '2024-11-01', 'Test', 'Completed'),
(4, 'India vs New Zealand, 2nd Test', 1, 6, 1, '2024-10-24', 'Test', 'Completed'),
(4, 'India vs New Zealand, 1st Test', 1, 6, 6, '2024-10-16', 'Test', 'Completed'),
(5, 'Australia vs South Africa, 3rd ODI', 2, 5, 7, '2024-09-11', 'ODI', 'Completed'),
(5, 'Australia vs South Africa, 2nd ODI', 2, 5, 9, '2024-09-08', 'ODI', 'Completed'),
(5, 'Australia vs South Africa, 1st ODI', 2, 5, 4, '2024-08-30', 'ODI', 'Completed'),
(3, 'England vs Pakistan, 4th T20I', 3, 4, 8, '2024-05-30', 'T20I', 'Completed'),
(3, 'England vs Pakistan, 3rd T20I', 3, 4, 3, '2024-05-28', 'T20I', 'Completed');

-- Insert Match Results
INSERT INTO match_results (match_id, winning_team_id, victory_margin, victory_type, man_of_the_match) VALUES
(1, 6, 25, 'runs', 11),
(2, 6, 113, 'runs', 11),
(3, 6, 8, 'wickets', 13),
(4, 2, 122, 'runs', 6),
(5, 5, 7, 'wickets', 14),
(6, 2, 35, 'runs', 7),
(7, 4, 6, 'wickets', 10),
(8, 3, 3, 'wickets', 8);

-- Insert Batting Performances
INSERT INTO batting_performances (match_id, player_id, team_id, innings_number, batting_position, runs_scored, balls_faced, fours, sixes, strike_rate) VALUES
-- Match 1: India vs New Zealand, 3rd Test
(1, 1, 1, 1, 3, 85, 124, 8, 1, 68.55),
(1, 2, 1, 1, 1, 52, 89, 6, 0, 58.43),
(1, 11, 6, 1, 4, 156, 245, 18, 2, 63.67),
-- Match 2: India vs New Zealand, 2nd Test  
(2, 1, 1, 1, 3, 44, 67, 4, 0, 65.67),
(2, 2, 1, 1, 1, 18, 43, 2, 0, 41.86),
(2, 11, 6, 1, 4, 134, 189, 14, 1, 70.90),
-- ODI Match performances
(4, 6, 2, 1, 3, 98, 85, 8, 2, 115.29),
(4, 14, 5, 1, 4, 67, 78, 5, 1, 85.90),
(5, 14, 5, 1, 4, 89, 94, 7, 2, 94.68),
(6, 6, 2, 1, 3, 76, 65, 6, 1, 116.92);

-- Insert Bowling Performances
INSERT INTO bowling_performances (match_id, player_id, team_id, innings_number, overs_bowled, runs_conceded, wickets_taken, economy_rate) VALUES
-- Test match bowling
(1, 3, 1, 1, 18.2, 45, 4, 2.45),
(1, 4, 1, 1, 22.0, 67, 2, 3.05),
(2, 3, 1, 1, 15.4, 38, 3, 2.43),
(2, 4, 1, 1, 19.0, 58, 1, 3.05),
-- ODI bowling
(4, 7, 2, 1, 9.0, 42, 2, 4.67),
(4, 15, 5, 1, 8.5, 56, 1, 6.35),
(5, 15, 5, 1, 10.0, 48, 3, 4.80),
(6, 7, 2, 1, 8.0, 35, 1, 4.38);

-- Additional sample data to support complex queries
-- More batting performances for partnership analysis
INSERT INTO batting_performances (match_id, player_id, team_id, innings_number, batting_position, runs_scored, balls_faced, fours, sixes, strike_rate) VALUES
-- Partnership data - consecutive batting positions
(1, 5, 1, 1, 4, 78, 112, 7, 1, 69.64), -- Position 4, pairs with Kohli at 3
(1, 4, 1, 1, 5, 65, 98, 5, 0, 66.33),  -- Position 5, pairs with Dhoni at 4
(4, 2, 2, 1, 1, 87, 76, 9, 2, 114.47), -- Rohit Sharma for Australia (guest player)
(4, 6, 2, 1, 2, 54, 48, 4, 1, 112.50); -- Consecutive positions

-- More bowling data for venue analysis
INSERT INTO bowling_performances (match_id, player_id, team_id, innings_number, overs_bowled, runs_conceded, wickets_taken, economy_rate) VALUES
-- Same bowlers at same venues for analysis
(3, 3, 1, 1, 16.0, 52, 2, 3.25), -- Bumrah at Narendra Modi Stadium
(6, 3, 1, 1, 8.0, 28, 1, 3.50),  -- Bumrah at MCG (different venue)
(1, 12, 6, 1, 20.0, 78, 3, 3.90), -- Trent Boult
(2, 12, 6, 1, 18.5, 65, 2, 3.45); -- Trent Boult again

-- Update career stats based on performances
UPDATE players SET 
    career_runs = (SELECT COALESCE(SUM(runs_scored), 0) FROM batting_performances WHERE player_id = players.player_id),
    career_wickets = (SELECT COALESCE(SUM(wickets_taken), 0) FROM bowling_performances WHERE player_id = players.player_id);

COMMIT;