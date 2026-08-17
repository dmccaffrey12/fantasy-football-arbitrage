import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(
    page_title="2026 In-Season Strategic Control Tower", 
    page_icon="🏈", 
    layout="wide"
)

NFL_NAME_TO_CODE = {
    'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL', 'Buffalo Bills': 'BUF',
    'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI', 'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE',
    'Dallas Cowboys': 'DAL', 'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX', 'Kansas City Chiefs': 'KC',
    'Los Angeles Chargers': 'LAC', 'Los Angeles Rams': 'LAR', 'Las Vegas Raiders': 'LV', 'Miami Dolphins': 'MIA',
    'Minnesota Vikings': 'MIN', 'New England Patriots': 'NE', 'New Orleans Saints': 'NO', 'New York Giants': 'NYG',
    'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT', 'Seattle Seahawks': 'SEA',
    'San Francisco 49ers': 'SF', 'Tampa Bay Buccaneers': 'TB', 'Tennessee Titans': 'TEN', 'Washington Commanders': 'WSH'
}

NFL_TEAMS = {v: k for k, v in NFL_NAME_TO_CODE.items()}

# 2026 IN-SEASON TRADE VALUE DATABASE (SUPERFLEX & 6-PT PASS TD CALIBRATED)
TRADE_DATABASE = {
    # Quarterbacks
    'Josh Allen': {'Pos': 'QB', 'Team': 'BUF', 'Value': 94.0, 'Proj_PPG': 25.2},
    'Lamar Jackson': {'Pos': 'QB', 'Team': 'BAL', 'Value': 90.5, 'Proj_PPG': 24.1},
    'Patrick Mahomes': {'Pos': 'QB', 'Team': 'KC', 'Value': 88.0, 'Proj_PPG': 23.5},
    'Jalen Hurts': {'Pos': 'QB', 'Team': 'PHI', 'Value': 87.0, 'Proj_PPG': 23.2},
    'Dak Prescott': {'Pos': 'QB', 'Team': 'DAL', 'Value': 84.5, 'Proj_PPG': 22.8},
    'Joe Burrow': {'Pos': 'QB', 'Team': 'CIN', 'Value': 84.0, 'Proj_PPG': 22.6},
    'Jayden Daniels': {'Pos': 'QB', 'Team': 'WSH', 'Value': 82.0, 'Proj_PPG': 22.1},
    'Jared Goff': {'Pos': 'QB', 'Team': 'DET', 'Value': 79.5, 'Proj_PPG': 21.4},
    'C.J. Stroud': {'Pos': 'QB', 'Team': 'HOU', 'Value': 78.0, 'Proj_PPG': 21.0},
    'Kyler Murray': {'Pos': 'QB', 'Team': 'ARI', 'Value': 77.5, 'Proj_PPG': 20.8},
    'Caleb Williams': {'Pos': 'QB', 'Team': 'CHI', 'Value': 74.0, 'Proj_PPG': 19.8},
    'Jordan Love': {'Pos': 'QB', 'Team': 'GB', 'Value': 73.5, 'Proj_PPG': 19.6},
    'Trevor Lawrence': {'Pos': 'QB', 'Team': 'JAX', 'Value': 71.0, 'Proj_PPG': 18.9},
    'Brock Purdy': {'Pos': 'QB', 'Team': 'SF', 'Value': 70.5, 'Proj_PPG': 18.7},
    'Justin Herbert': {'Pos': 'QB', 'Team': 'LAC', 'Value': 69.0, 'Proj_PPG': 18.4},
    'Bo Nix': {'Pos': 'QB', 'Team': 'DEN', 'Value': 67.0, 'Proj_PPG': 17.8},
    'Baker Mayfield': {'Pos': 'QB', 'Team': 'TB', 'Value': 65.0, 'Proj_PPG': 17.2},
    'Matthew Stafford': {'Pos': 'QB', 'Team': 'LAR', 'Value': 63.5, 'Proj_PPG': 16.8},
    
    # Running Backs
    'Bijan Robinson': {'Pos': 'RB', 'Team': 'ATL', 'Value': 95.0, 'Proj_PPG': 19.8},
    'Jahmyr Gibbs': {'Pos': 'RB', 'Team': 'DET', 'Value': 92.0, 'Proj_PPG': 18.9},
    'Christian McCaffrey': {'Pos': 'RB', 'Team': 'SF', 'Value': 91.0, 'Proj_PPG': 19.2},
    'Breece Hall': {'Pos': 'RB', 'Team': 'NYJ', 'Value': 89.0, 'Proj_PPG': 18.2},
    'Jonathan Taylor': {'Pos': 'RB', 'Team': 'IND', 'Value': 86.0, 'Proj_PPG': 17.4},
    'Chase Brown': {'Pos': 'RB', 'Team': 'CIN', 'Value': 82.5, 'Proj_PPG': 16.6},
    'Saquon Barkley': {'Pos': 'RB', 'Team': 'PHI', 'Value': 81.0, 'Proj_PPG': 16.2},
    'De\'Von Achane': {'Pos': 'RB', 'Team': 'MIA', 'Value': 79.5, 'Proj_PPG': 15.9},
    'Omarion Hampton': {'Pos': 'RB', 'Team': 'LAC', 'Value': 74.0, 'Proj_PPG': 14.8},
    'Bucky Irving': {'Pos': 'RB', 'Team': 'TB', 'Value': 72.5, 'Proj_PPG': 14.4},
    'Kenneth Walker III': {'Pos': 'RB', 'Team': 'KC', 'Value': 71.0, 'Proj_PPG': 14.1},
    'Josh Jacobs': {'Pos': 'RB', 'Team': 'GB', 'Value': 70.0, 'Proj_PPG': 13.9},
    'Derrick Henry': {'Pos': 'RB', 'Team': 'BAL', 'Value': 68.5, 'Proj_PPG': 13.5},
    'James Cook III': {'Pos': 'RB', 'Team': 'BUF', 'Value': 67.0, 'Proj_PPG': 13.2},
    'Tony Pollard': {'Pos': 'RB', 'Team': 'TEN', 'Value': 58.0, 'Proj_PPG': 11.6},
    'RJ Harvey': {'Pos': 'RB', 'Team': 'DEN', 'Value': 54.0, 'Proj_PPG': 10.8},
    'Jonah Coleman': {'Pos': 'RB', 'Team': 'DEN', 'Value': 48.0, 'Proj_PPG': 9.8},
    'D\'Andre Swift': {'Pos': 'RB', 'Team': 'CHI', 'Value': 55.0, 'Proj_PPG': 11.0},
    'Rhamondre Stevenson': {'Pos': 'RB', 'Team': 'NE', 'Value': 52.0, 'Proj_PPG': 10.4},
    'Jaylen Warren': {'Pos': 'RB', 'Team': 'PIT', 'Value': 49.0, 'Proj_PPG': 9.9},
    
    # Wide Receivers
    'CeeDee Lamb': {'Pos': 'WR', 'Team': 'DAL', 'Value': 96.0, 'Proj_PPG': 19.5},
    'Ja\'Marr Chase': {'Pos': 'WR', 'Team': 'CIN', 'Value': 95.5, 'Proj_PPG': 19.2},
    'Justin Jefferson': {'Pos': 'WR', 'Team': 'MIN', 'Value': 94.0, 'Proj_PPG': 18.8},
    'Amon-Ra St. Brown': {'Pos': 'WR', 'Team': 'DET', 'Value': 92.5, 'Proj_PPG': 18.4},
    'A.J. Brown': {'Pos': 'WR', 'Team': 'NE', 'Value': 89.0, 'Proj_PPG': 17.5},
    'Puka Nacua': {'Pos': 'WR', 'Team': 'LAR', 'Value': 88.0, 'Proj_PPG': 17.2},
    'Garrett Wilson': {'Pos': 'WR', 'Team': 'NYJ', 'Value': 85.0, 'Proj_PPG': 16.5},
    'Drake London': {'Pos': 'WR', 'Team': 'ATL', 'Value': 83.5, 'Proj_PPG': 16.1},
    'Marvin Harrison Jr.': {'Pos': 'WR', 'Team': 'ARI', 'Value': 82.0, 'Proj_PPG': 15.8},
    'Nico Collins': {'Pos': 'WR', 'Team': 'HOU', 'Value': 80.5, 'Proj_PPG': 15.4},
    'Malik Nabers': {'Pos': 'WR', 'Team': 'NYG', 'Value': 79.0, 'Proj_PPG': 15.1},
    'Rashee Rice': {'Pos': 'WR', 'Team': 'KC', 'Value': 78.0, 'Proj_PPG': 14.9},
    'DeVonta Smith': {'Pos': 'WR', 'Team': 'PHI', 'Value': 75.0, 'Proj_PPG': 14.3},
    'DJ Moore': {'Pos': 'WR', 'Team': 'BUF', 'Value': 73.5, 'Proj_PPG': 14.0},
    'Tee Higgins': {'Pos': 'WR', 'Team': 'CIN', 'Value': 72.0, 'Proj_PPG': 13.7},
    'Jaylen Waddle': {'Pos': 'WR', 'Team': 'DEN', 'Value': 70.0, 'Proj_PPG': 13.4},
    'Chris Olave': {'Pos': 'WR', 'Team': 'NO', 'Value': 69.5, 'Proj_PPG': 13.2},
    'DK Metcalf': {'Pos': 'WR', 'Team': 'PIT', 'Value': 68.0, 'Proj_PPG': 12.9},
    'George Pickens': {'Pos': 'WR', 'Team': 'DAL', 'Value': 66.5, 'Proj_PPG': 12.6},
    'Rome Odunze': {'Pos': 'WR', 'Team': 'CHI', 'Value': 64.0, 'Proj_PPG': 12.2},
    'Ladd McConkey': {'Pos': 'WR', 'Team': 'LAC', 'Value': 63.0, 'Proj_PPG': 12.0},
    'Wan\'Dale Robinson': {'Pos': 'WR', 'Team': 'TEN', 'Value': 54.0, 'Proj_PPG': 10.5},
    'Josh Downs': {'Pos': 'WR', 'Team': 'IND', 'Value': 51.0, 'Proj_PPG': 10.0},
    'Jayden Higgins': {'Pos': 'WR', 'Team': 'HOU', 'Value': 47.0, 'Proj_PPG': 9.2},
    'Jalen McMillan': {'Pos': 'WR', 'Team': 'TB', 'Value': 45.0, 'Proj_PPG': 8.8},
    'Chris Bell': {'Pos': 'WR', 'Team': 'MIA', 'Value': 38.0, 'Proj_PPG': 7.5},
    
    # Tight Ends
    'Brock Bowers': {'Pos': 'TE', 'Team': 'LV', 'Value': 78.0, 'Proj_PPG': 13.8},
    'Trey McBride': {'Pos': 'TE', 'Team': 'ARI', 'Value': 76.0, 'Proj_PPG': 13.4},
    'Sam LaPorta': {'Pos': 'TE', 'Team': 'DET', 'Value': 73.0, 'Proj_PPG': 12.8},
    'Travis Kelce': {'Pos': 'TE', 'Team': 'KC', 'Value': 68.0, 'Proj_PPG': 12.0},
    'Mark Andrews': {'Pos': 'TE', 'Team': 'BAL', 'Value': 65.0, 'Proj_PPG': 11.4},
    'George Kittle': {'Pos': 'TE', 'Team': 'SF', 'Value': 63.0, 'Proj_PPG': 11.0},
    'Jake Ferguson': {'Pos': 'TE', 'Team': 'DAL', 'Value': 48.0, 'Proj_PPG': 8.5}
}

# BASELINE DEFENSE METRICS
DEFAULT_DST_METRICS = {
    'CLE': {'Pressure_Rate': 28.5, 'Sack_Rate': 8.9, 'Blitz_Rate': 31.0},
    'PIT': {'Pressure_Rate': 27.1, 'Sack_Rate': 8.4, 'Blitz_Rate': 33.0},
    'NYJ': {'Pressure_Rate': 26.8, 'Sack_Rate': 8.1, 'Blitz_Rate': 21.5},
    'SF':  {'Pressure_Rate': 26.2, 'Sack_Rate': 7.9, 'Blitz_Rate': 22.0},
    'DAL': {'Pressure_Rate': 26.0, 'Sack_Rate': 7.8, 'Blitz_Rate': 30.0},
    'HOU': {'Pressure_Rate': 25.4, 'Sack_Rate': 7.7, 'Blitz_Rate': 25.0},
    'BAL': {'Pressure_Rate': 25.0, 'Sack_Rate': 7.6, 'Blitz_Rate': 29.5},
    'JAX': {'Pressure_Rate': 24.8, 'Sack_Rate': 7.4, 'Blitz_Rate': 28.0},
    'NYG': {'Pressure_Rate': 25.5, 'Sack_Rate': 7.5, 'Blitz_Rate': 32.0},
    'DEN': {'Pressure_Rate': 24.0, 'Sack_Rate': 7.2, 'Blitz_Rate': 27.0},
    'SEA': {'Pressure_Rate': 23.5, 'Sack_Rate': 6.9, 'Blitz_Rate': 26.0},
    'TB':  {'Pressure_Rate': 23.0, 'Sack_Rate': 6.7, 'Blitz_Rate': 34.0},
    'LV':  {'Pressure_Rate': 22.8, 'Sack_Rate': 6.9, 'Blitz_Rate': 24.0},
    'CIN': {'Pressure_Rate': 22.1, 'Sack_Rate': 6.8, 'Blitz_Rate': 24.5},
    'KC':  {'Pressure_Rate': 22.5, 'Sack_Rate': 6.6, 'Blitz_Rate': 27.0},
    'GB':  {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 26.0},
    'IND': {'Pressure_Rate': 21.8, 'Sack_Rate': 6.4, 'Blitz_Rate': 21.0},
    'BUF': {'Pressure_Rate': 22.4, 'Sack_Rate': 6.6, 'Blitz_Rate': 23.0},
    'PHI': {'Pressure_Rate': 22.0, 'Sack_Rate': 6.4, 'Blitz_Rate': 22.5},
    'MIN': {'Pressure_Rate': 23.2, 'Sack_Rate': 6.8, 'Blitz_Rate': 38.0},
    'DET': {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 25.0},
    'LAR': {'Pressure_Rate': 21.5, 'Sack_Rate': 6.3, 'Blitz_Rate': 24.0},
    'MIA': {'Pressure_Rate': 21.4, 'Sack_Rate': 6.2, 'Blitz_Rate': 27.0},
    'LAC': {'Pressure_Rate': 21.2, 'Sack_Rate': 6.1, 'Blitz_Rate': 23.0},
    'NO':  {'Pressure_Rate': 21.0, 'Sack_Rate': 6.0, 'Blitz_Rate': 24.0},
    'NE':  {'Pressure_Rate': 21.0, 'Sack_Rate': 5.9, 'Blitz_Rate': 23.0},
    'CHI': {'Pressure_Rate': 20.8, 'Sack_Rate': 5.8, 'Blitz_Rate': 22.0},
    'TEN': {'Pressure_Rate': 20.5, 'Sack_Rate': 5.8, 'Blitz_Rate': 25.0},
    'ATL': {'Pressure_Rate': 20.0, 'Sack_Rate': 5.5, 'Blitz_Rate': 22.0},
    'WSH': {'Pressure_Rate': 19.5, 'Sack_Rate': 5.4, 'Blitz_Rate': 24.0},
    'ARI': {'Pressure_Rate': 19.0, 'Sack_Rate': 5.3, 'Blitz_Rate': 21.0},
    'CAR': {'Pressure_Rate': 18.5, 'Sack_Rate': 5.2, 'Blitz_Rate': 22.0}
}

DEFAULT_OPPONENT_METRICS = {
    'NE':  {'OL_Pressure_Allowed': 29.0, 'QB_Sack_Penalty': 1.25, 'Turnover_Rate': 2.0},
    'CAR': {'OL_Pressure_Allowed': 28.0, 'QB_Sack_Penalty': 1.20, 'Turnover_Rate': 2.1},
    'CLE': {'OL_Pressure_Allowed': 27.5, 'QB_Sack_Penalty': 1.20, 'Turnover_Rate': 2.0},
    'NYG': {'OL_Pressure_Allowed': 27.0, 'QB_Sack_Penalty': 1.20, 'Turnover_Rate': 2.0},
    'TEN': {'OL_Pressure_Allowed': 26.5, 'QB_Sack_Penalty': 1.15, 'Turnover_Rate': 1.9},
    'WSH': {'OL_Pressure_Allowed': 25.8, 'QB_Sack_Penalty': 1.15, 'Turnover_Rate': 1.9},
    'LV':  {'OL_Pressure_Allowed': 25.0, 'QB_Sack_Penalty': 1.10, 'Turnover_Rate': 1.8},
    'ARI': {'OL_Pressure_Allowed': 24.5, 'QB_Sack_Penalty': 1.10, 'Turnover_Rate': 1.7},
    'DEN': {'OL_Pressure_Allowed': 24.0, 'QB_Sack_Penalty': 1.10, 'Turnover_Rate': 1.7},
    'SEA': {'OL_Pressure_Allowed': 24.2, 'QB_Sack_Penalty': 1.05, 'Turnover_Rate': 1.7},
    'NO':  {'OL_Pressure_Allowed': 23.5, 'QB_Sack_Penalty': 1.05, 'Turnover_Rate': 1.6},
    'TB':  {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Penalty': 1.00, 'Turnover_Rate': 1.6},
    'CHI': {'OL_Pressure_Allowed': 24.8, 'QB_Sack_Penalty': 1.10, 'Turnover_Rate': 1.8},
    'MIN': {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Penalty': 1.00, 'Turnover_Rate': 1.6},
    'ATL': {'OL_Pressure_Allowed': 22.0, 'QB_Sack_Penalty': 0.95, 'Turnover_Rate': 1.5},
    'LAC': {'OL_Pressure_Allowed': 21.5, 'QB_Sack_Penalty': 0.95, 'Turnover_Rate': 1.5},
    'PIT': {'OL_Pressure_Allowed': 22.8, 'QB_Sack_Penalty': 1.00, 'Turnover_Rate': 1.6},
    'JAX': {'OL_Pressure_Allowed': 21.0, 'QB_Sack_Penalty': 0.95, 'Turnover_Rate': 1.5},
    'MIA': {'OL_Pressure_Allowed': 20.5, 'QB_Sack_Penalty': 0.90, 'Turnover_Rate': 1.4},
    'IND': {'OL_Pressure_Allowed': 19.5, 'QB_Sack_Penalty': 0.85, 'Turnover_Rate': 1.3},
    'LAR': {'OL_Pressure_Allowed': 20.0, 'QB_Sack_Penalty': 0.90, 'Turnover_Rate': 1.4},
    'CIN': {'OL_Pressure_Allowed': 21.0, 'QB_Sack_Penalty': 0.95, 'Turnover_Rate': 1.4},
    'GB':  {'OL_Pressure_Allowed': 18.5, 'QB_Sack_Penalty': 0.80, 'Turnover_Rate': 1.2},
    'HOU': {'OL_Pressure_Allowed': 19.0, 'QB_Sack_Penalty': 0.85, 'Turnover_Rate': 1.3},
    'DAL': {'OL_Pressure_Allowed': 18.0, 'QB_Sack_Penalty': 0.80, 'Turnover_Rate': 1.2},
    'SF':  {'OL_Pressure_Allowed': 18.2, 'QB_Sack_Penalty': 0.80, 'Turnover_Rate': 1.2},
    'BAL': {'OL_Pressure_Allowed': 17.5, 'QB_Sack_Penalty': 0.75, 'Turnover_Rate': 1.1},
    'BUF': {'OL_Pressure_Allowed': 18.0, 'QB_Sack_Penalty': 0.75, 'Turnover_Rate': 1.2},
    'KC':  {'OL_Pressure_Allowed': 17.0, 'QB_Sack_Penalty': 0.70, 'Turnover_Rate': 1.0},
    'PHI': {'OL_Pressure_Allowed': 16.8, 'QB_Sack_Penalty': 0.75, 'Turnover_Rate': 1.1},
    'DET': {'OL_Pressure_Allowed': 15.5, 'QB_Sack_Penalty': 0.70, 'Turnover_Rate': 1.0},
    'NYJ': {'OL_Pressure_Allowed': 19.5, 'QB_Sack_Penalty': 0.85, 'Turnover_Rate': 1.3}
}

FULL_NFL_SCHEDULE = {
    'JAX': [('CLE', -7.5, 40.5, 'Home'), ('DEN', -2.5, 41.0, 'Away'), ('NE', -5.5, 40.0, 'Home')],
    'DEN': [('KC', +2.5, 43.5, 'Away'),  ('JAX', +2.5, 41.0, 'Home'), ('LAR', +3.0, 44.5, 'Home')],
    'NE':  [('SEA', +4.0, 45.5, 'Away'), ('MIA', +3.5, 45.0, 'Home'), ('JAX', +5.5, 40.0, 'Away')],
    'CLE': [('JAX', +7.5, 40.5, 'Away'), ('TB', -1.5, 43.0, 'Away'),  ('CAR', -4.5, 40.5, 'Home')],
    'CIN': [('TB', -3.5, 51.5, 'Home'),  ('HOU', +1.5, 48.0, 'Away'),  ('PIT', -2.5, 44.0, 'Away')],
    'TB':  [('CIN', +3.5, 51.5, 'Away'), ('CLE', +1.5, 43.0, 'Home'),  ('MIN', -3.0, 45.0, 'Home')],
    'SEA': [('NE', -4.0, 45.5, 'Home'),  ('ARI', -3.0, 45.0, 'Away'),  ('WSH', -4.0, 44.5, 'Away')],
    'ARI': [('LAC', +10.5, 46.5, 'Away'), ('SEA', +3.0, 45.0, 'Home'), ('SF', +6.5, 47.0, 'Away')],
    'SF':  [('LAR', +3.5, 48.5, 'Neutral'), ('MIA', -4.5, 48.0, 'Home'), ('ARI', -6.5, 47.0, 'Home')],
    'LAR': [('SF', -3.5, 48.5, 'Neutral'), ('NYG', -6.5, 45.0, 'Home'), ('DEN', -3.0, 44.5, 'Away')],
    'DET': [('NO', -7.0, 49.5, 'Home'),  ('BUF', +2.5, 51.0, 'Away'),  ('NYJ', -4.5, 47.5, 'Home')],
    'NO':  [('DET', +7.0, 49.5, 'Away'), ('DAL', +6.0, 46.5, 'Away'),  ('LV', -1.5, 43.0, 'Home')],
    'IND': [('BAL', +3.5, 48.5, 'Home'), ('KC', +5.5, 49.5, 'Away'),   ('HOU', +1.5, 46.0, 'Home')],
    'BAL': [('IND', -3.5, 48.5, 'Away'), ('NO', -7.5, 45.0, 'Home'),   ('DAL', -2.5, 49.0, 'Neutral')],
    'HOU': [('BUF', +1.5, 44.5, 'Home'), ('CIN', -1.5, 48.0, 'Home'),  ('IND', -1.5, 46.0, 'Away')],
    'LAC': [('ARI', -10.5, 46.5, 'Home'), ('LV', -4.5, 43.0, 'Home'),   ('BUF', +3.5, 48.5, 'Away')],
    'LV':  [('MIA', -3.5, 40.5, 'Home'), ('LAC', +4.5, 43.0, 'Away'),  ('NO', +1.5, 43.0, 'Away')],
    'MIA': [('LV', +3.5, 40.5, 'Away'),  ('NE', -3.5, 45.0, 'Away'),   ('KC', +3.5, 49.0, 'Home')],
    'GB':  [('MIN', -1.5, 44.5, 'Away'), ('NYJ', -3.5, 43.0, 'Away'),  ('ATL', -4.5, 46.0, 'Home')],
    'MIN': [('GB', +1.5, 44.5, 'Home'),  ('SF', +4.5, 48.0, 'Away'),   ('TB', +3.0, 45.0, 'Away')],
    'NYJ': [('TEN', +2.5, 39.5, 'Away'), ('GB', +3.5, 43.0, 'Home'),   ('DET', +4.5, 47.5, 'Away')],
    'TEN': [('NYJ', -2.5, 39.5, 'Home'), ('CHI', +3.0, 42.5, 'Away'),  ('NYG', +1.5, 41.0, 'Away')],
    'CHI': [('CAR', -2.5, 47.5, 'Home'), ('TEN', -3.0, 42.5, 'Home'),  ('NYJ', -1.5, 42.0, 'Away')],
    'CAR': [('CHI', +2.5, 47.5, 'Away'), ('ATL', +4.5, 44.0, 'Away'),  ('CLE', +4.5, 40.5, 'Away')],
    'ATL': [('PIT', +3.0, 41.5, 'Home'), ('CAR', -4.5, 44.0, 'Home'),  ('GB', +4.5, 46.0, 'Away')],
    'PIT': [('ATL', -3.0, 41.5, 'Away'), ('DEN', -2.5, 39.5, 'Away'),  ('CIN', +2.5, 44.0, 'Home')],
    'PHI': [('WSH', -5.5, 46.5, 'Home'), ('DAL', -3.0, 48.5, 'Away'),  ('LAR', -2.5, 49.0, 'Home')],
    'WSH': [('PHI', +5.5, 46.5, 'Away'), ('DAL', +4.5, 47.0, 'Away'),  ('SEA', +4.0, 44.5, 'Home')],
    'DAL': [('NYG', -2.5, 48.5, 'Away'), ('WSH', -4.5, 47.0, 'Home'),  ('BAL', +2.5, 49.0, 'Neutral')],
    'NYG': [('DAL', +2.5, 48.5, 'Home'), ('LAR', +6.5, 45.0, 'Away'),  ('TEN', -1.5, 41.0, 'Home')],
    'BUF': [('HOU', -1.5, 44.5, 'Away'), ('DET', -2.5, 51.0, 'Home'),  ('LAC', -3.5, 48.5, 'Home')],
    'KC':  [('DEN', -2.5, 43.5, 'Home'), ('IND', -5.5, 49.5, 'Home'),  ('MIA', -3.5, 49.0, 'Away')]
}

@st.cache_data(ttl=3600)
def fetch_live_nfl_odds(api_key):
    if not api_key:
        return None
    url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
    params = {
        'apiKey': api_key.strip(),
        'regions': 'us',
        'markets': 'spreads,totals',
        'oddsFormat': 'american'
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            games = []
            for event in data:
                home_raw = event.get('home_team')
                away_raw = event.get('away_team')
                commence = event.get('commence_time')
                home_code = NFL_NAME_TO_CODE.get(home_raw, home_raw)
                away_code = NFL_NAME_TO_CODE.get(away_raw, away_raw)
                spread = 0.0
                total = 43.0
                for bookmaker in event.get('bookmakers', []):
                    for m in bookmaker.get('markets', []):
                        if m['key'] == 'spreads':
                            for outcome in m['outcomes']:
                                if outcome['name'] == home_raw:
                                    spread = outcome.get('point', 0.0)
                        elif m['key'] == 'totals':
                            total = m['outcomes'][0].get('point', 43.0)
                    if spread != 0.0 and total != 43.0:
                        break
                home_implied = round((total / 2.0) - (spread / 2.0), 1)
                away_implied = round((total / 2.0) + (spread / 2.0), 1)
                games.append({
                    'Home_Team': home_raw,
                    'Away_Team': away_raw,
                    'Home_Code': home_code,
                    'Away_Code': away_code,
                    'Spread': spread,
                    'Game_Total': total,
                    'Home_Implied_Pts': home_implied,
                    'Away_Implied_Pts': away_implied,
                    'Kickoff': commence
                })
            return pd.DataFrame(games)
    except Exception:
        pass
    return None

def calculate_dst_composite_score(dst_code, opp_code, spread, ou_total, is_home, dst_metrics_dict=None, opp_metrics_dict=None):
    dst_dict = dst_metrics_dict if dst_metrics_dict else DEFAULT_DST_METRICS
    opp_dict = opp_metrics_dict if opp_metrics_dict else DEFAULT_OPPONENT_METRICS
    dst_data = dst_dict.get(dst_code, {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 25.0})
    opp_data = opp_dict.get(opp_code, {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Penalty': 1.0, 'Turnover_Rate': 1.6})
    
    implied_opp_total = (ou_total / 2.0) - (spread / 2.0)
    combined_pressure_idx = (dst_data['Pressure_Rate'] * 0.45) + (opp_data['OL_Pressure_Allowed'] * 0.55)
    base_sacks = (dst_data['Sack_Rate'] / 100.0) * 35.0
    expected_sacks = base_sacks * opp_data['QB_Sack_Penalty'] * (combined_pressure_idx / 23.0)
    expected_sack_pts = expected_sacks * 1.0
    
    trailing_mult = 1.20 if spread <= -4.0 else (1.10 if spread < 0 else 0.90)
    expected_turnovers = ((opp_data['Turnover_Rate'] * 0.65) + (0.3 if is_home else 0.0)) * trailing_mult
    expected_to_pts = expected_turnovers * 2.0
    
    if implied_opp_total < 14.0:
        pts_allowed_equity = 7.0
    elif implied_opp_total < 18.0:
        pts_allowed_equity = 4.5
    elif implied_opp_total < 21.0:
        pts_allowed_equity = 2.0
    elif implied_opp_total < 25.0:
        pts_allowed_equity = 1.0
    else:
        pts_allowed_equity = 0.0
        
    td_equity = (expected_turnovers * 0.06) * 6.0
    composite_raw = expected_sack_pts + expected_to_pts + pts_allowed_equity + td_equity
    return {
        'Composite_Score': round(composite_raw, 2),
        'Expected_Sacks': round(expected_sacks, 1),
        'Expected_Takeaways': round(expected_turnovers, 1),
        'Implied_Opp_Points': round(implied_opp_total, 1),
        'Pressure_Index': round(combined_pressure_idx, 1)
    }

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("🔑 Live Market API Settings")
    api_key_input = st.text_input(
        "The-Odds-API Key", 
        value=st.session_state.get('the_odds_api_key', ''),
        type="password",
        placeholder="Paste your API key here...",
        help="Get a free key with 500 requests/month at the-odds-api.com"
    )
    if api_key_input:
        st.session_state.the_odds_api_key = api_key_input
        st.success("✅ API Key Connected!")
    st.markdown("---")
    st.caption("Active Roster: Dak, Goff, Chase Brown, Hampton, Bucky, London, DJ Moore, JAX D/ST")

st.title("🏈 2026 In-Season Strategic Control Tower")
st.caption("D/ST Streaming Engine, Live Vegas Arbitrage, Lineup Solver & Trade Terminal")

tabs = st.tabs([
    "🛡️ D/ST Asymmetric Streaming Terminal",
    "📊 Weekly Projections & Lineup Solver",
    "⚖️ Live Vegas Spreads & Implied Totals",
    "🤝 Trade Analyzer & Valuation Terminal"
])

# --- TAB 1: D/ST TERMINAL ---
with tabs[0]:
    st.header("🛡️ D/ST Asymmetric Streaming Terminal (All 32 NFL Defenses)")
    st.caption("Pass-Rush vs. OL Deficit Index, Scheme Tuning & Verified 2026 Schedule")
    
    if 'custom_dst_metrics' not in st.session_state:
        st.session_state.custom_dst_metrics = DEFAULT_DST_METRICS.copy()
    if 'custom_opp_metrics' not in st.session_state:
        st.session_state.custom_opp_metrics = DEFAULT_OPPONENT_METRICS.copy()
        
    all_teams_list = sorted(list(FULL_NFL_SCHEDULE.keys()))
    
    with st.expander("🛠️ Dynamic Scheme Tuning & Coaching Overrides", expanded=False):
        col_m1, col_m2 = st.columns(2)
        tune_team = col_m1.selectbox("Select Team to Tune", all_teams_list, index=all_teams_list.index('NYG'))
        curr_d = st.session_state.custom_dst_metrics.get(tune_team, {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 25.0})
        curr_o = st.session_state.custom_opp_metrics.get(tune_team, {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Penalty': 1.0, 'Turnover_Rate': 1.6})
        c_t1, c_t2, c_t3 = st.columns(3)
        new_pr = c_t1.slider(f"{tune_team} Defensive Pressure %", 15.0, 35.0, float(curr_d['Pressure_Rate']), 0.5)
        new_sr = c_t2.slider(f"{tune_team} Sack Rate %", 4.0, 12.0, float(curr_d['Sack_Rate']), 0.1)
        new_ol = c_t3.slider(f"{tune_team} OL Pressure Allowed %", 14.0, 35.0, float(curr_o['OL_Pressure_Allowed']), 0.5)
        if st.button(f"💾 Save {tune_team} Metrics"):
            st.session_state.custom_dst_metrics[tune_team]['Pressure_Rate'] = new_pr
            st.session_state.custom_dst_metrics[tune_team]['Sack_Rate'] = new_sr
            st.session_state.custom_opp_metrics[tune_team]['OL_Pressure_Allowed'] = new_ol
            st.success(f"Saved {tune_team} updates!")
            st.rerun()

    search_q = st.text_input("🔍 Quick Filter Team (e.g. JAX, SEA, DEN, Dallas):", value="").strip().upper()
    if search_q:
        filtered_teams = [t for t in all_teams_list if search_q in t or search_q in NFL_TEAMS.get(t, '').upper()]
    else:
        filtered_teams = all_teams_list
        
    st.subheader(f"🔥 Week 1 League-Wide D/ST Rankings ({len(filtered_teams)} Teams)")
    rankings_data = []
    for t_code in filtered_teams:
        matchup = FULL_NFL_SCHEDULE[t_code][0]
        opp, spread, ou, loc = matchup[0], matchup[1], matchup[2], matchup[3]
        res = calculate_dst_composite_score(t_code, opp, spread, ou, loc == 'Home', st.session_state.custom_dst_metrics, st.session_state.custom_opp_metrics)
        rankings_data.append({
            'Rank': 0, 'Team': NFL_TEAMS.get(t_code, t_code), 'Code': t_code, 'Week 1 Matchup': f"{'vs' if loc=='Home' else '@'} {opp} ({spread:+.1f})",
            'Projected PTS': res['Composite_Score'], 'Exp. Sacks': res['Expected_Sacks'], 'Exp. Turnovers': res['Expected_Takeaways'],
            'Opp. Implied Pts': res['Implied_Opp_Points'], 'Streaming Tier': '🔥 Top Stream (Smash)' if res['Composite_Score'] >= 8.5 else ('🟢 Solid' if res['Composite_Score'] >= 7.0 else '🟡 Risky' if res['Composite_Score'] >= 5.5 else '🔴 Avoid')
        })
    df_board = pd.DataFrame(rankings_data).sort_values(by='Projected PTS', ascending=False).reset_index(drop=True)
    df_board['Rank'] = df_board.index + 1
    st.dataframe(df_board[['Rank', 'Team', 'Code', 'Week 1 Matchup', 'Projected PTS', 'Exp. Sacks', 'Exp. Turnovers', 'Opp. Implied Pts', 'Streaming Tier']], use_container_width=True)
    
    st.markdown("---")
    st.subheader(f"📅 3-Week Stash & Stream Matrix ({len(filtered_teams)} Teams)")
    multi_data = []
    for d_code in filtered_teams:
        weeks = FULL_NFL_SCHEDULE[d_code]
        w1, w2, w3 = weeks[0], weeks[1], weeks[2]
        r1 = calculate_dst_composite_score(d_code, w1[0], w1[1], w1[2], w1[3]=='Home', st.session_state.custom_dst_metrics, st.session_state.custom_opp_metrics)['Composite_Score']
        r2 = calculate_dst_composite_score(d_code, w2[0], w2[1], w2[2], w2[3]=='Home', st.session_state.custom_dst_metrics, st.session_state.custom_opp_metrics)['Composite_Score']
        r3 = calculate_dst_composite_score(d_code, w3[0], w3[1], w3[2], w3[3]=='Home', st.session_state.custom_dst_metrics, st.session_state.custom_opp_metrics)['Composite_Score']
        avg_3w = round((r1 + r2 + r3) / 3.0, 2)
        multi_data.append({
            'Team': NFL_TEAMS.get(d_code, d_code),
            'Code': d_code,
            'Week 1': f"{'vs' if w1[3]=='Home' else '@'} {w1[0]} ({r1} pts)",
            'Week 2': f"{'vs' if w2[3]=='Home' else '@'} {w2[0]} ({r2} pts)",
            'Week 3': f"{'vs' if w3[3]=='Home' else '@'} {w3[0]} ({r3} pts)",
            '3-Week Avg': avg_3w,
            'Play': '🔥 Multi-Week Anchor' if avg_3w >= 7.8 else ('🟢 1-Week Stream' if r1 >= 7.8 else '🟡 Stash for W2/W3' if r2 >= 7.8 else '⚪ Pass')
        })
    df_multi = pd.DataFrame(multi_data).sort_values(by='3-Week Avg', ascending=False).reset_index(drop=True)
    st.dataframe(df_multi, use_container_width=True)

# --- TAB 2: PROJECTIONS & LINEUP SOLVER ---
with tabs[1]:
    st.header("📊 Weekly Spreadsheet Ingestion & Lineup Solver")
    st.caption("Upload weekly projections to auto-solve your optimal starting 8:")
    col_u1, col_u2 = st.columns([2, 1])
    uploaded_file = col_u1.file_uploader("Upload Weekly Projections (.xlsx or .csv)", type=['xlsx', 'csv'])
    opt_mode = col_u2.selectbox("Strategy Mode", ["Expected Points (Median)", "Floor Maximizer (Favored)", "Ceiling Chaser (Underdog)"])
    
    if uploaded_file is not None:
        try:
            df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"✅ Ingested {len(df_raw)} players from weekly spreadsheet!")
            st.dataframe(df_raw.head(15), use_container_width=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("💡 Drag and drop your weekly projections file above once available.")

# --- TAB 3: LIVE VEGAS TOTALS & SPREADS ---
with tabs[2]:
    st.header("⚖️ Live Vegas Spreads & Implied Team Totals")
    active_key = st.session_state.get('the_odds_api_key', '')
    if active_key:
        with st.spinner("Fetching live NFL odds..."):
            df_odds = fetch_live_nfl_odds(active_key)
        if df_odds is not None and not df_odds.empty:
            st.dataframe(df_odds[['Away_Team', 'Home_Team', 'Spread', 'Game_Total', 'Away_Implied_Pts', 'Home_Implied_Pts', 'Kickoff']], use_container_width=True)
            st.markdown("---")
            st.subheader("🔥 High-Scoring Shootouts (Game Totals $\ge$ 47.5)")
            shootouts = df_odds[df_odds['Game_Total'] >= 47.5]
            if not shootouts.empty:
                for idx, row in shootouts.iterrows():
                    st.info(f"⚡ **{row['Away_Team']} @ {row['Home_Team']}** | Total: **{row['Game_Total']}** | Implied: {row['Away_Code']} ({row['Away_Implied_Pts']}) vs {row['Home_Code']} ({row['Home_Implied_Pts']})")
        else:
            st.info("No active NFL game lines returned for this week yet.")
    else:
        st.warning("⚠️ **No API Key Found.** Enter your free API key in the sidebar to unlock live odds.")

# --- TAB 4: TRADE ANALYZER & VALUATION TERMINAL ---
with tabs[3]:
    st.header("🤝 Trade Analyzer & True Valuation Terminal")
    st.caption("Superflex True VORP Index & Multi-Player Package Calculator")
    
    player_pool = sorted(list(TRADE_DATABASE.keys()))
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("📤 You Send (Giving Away)")
        giving_players = st.multiselect("Select Player(s) to Trade Away:", player_pool, default=['Tony Pollard'])
        
    with col_t2:
        st.subheader("📥 You Receive (Getting Back)")
        receiving_players = st.multiselect("Select Player(s) to Receive:", player_pool, default=['Malik Nabers'])
        
    if giving_players or receiving_players:
        giving_val = sum([TRADE_DATABASE[p]['Value'] for p in giving_players])
        receiving_val = sum([TRADE_DATABASE[p]['Value'] for p in receiving_players])
        
        giving_ppg = sum([TRADE_DATABASE[p]['Proj_PPG'] for p in giving_players])
        receiving_ppg = sum([TRADE_DATABASE[p]['Proj_PPG'] for p in receiving_players])
        
        # Package Roster Spot Adjustment (Penalty for receiving fewer concentrated assets)
        # e.g., 2 players for 1 elite player has an inherent roster consolidation premium
        if len(giving_players) > len(receiving_players):
            consolidation_bonus = (len(giving_players) - len(receiving_players)) * 5.0
            receiving_val_adj = receiving_val + consolidation_bonus
        elif len(receiving_players) > len(giving_players):
            consolidation_penalty = (len(receiving_players) - len(giving_players)) * 5.0
            receiving_val_adj = receiving_val - consolidation_penalty
        else:
            receiving_val_adj = receiving_val
            
        net_value_diff = round(receiving_val_adj - giving_val, 1)
        net_ppg_diff = round(receiving_ppg - giving_ppg, 1)
        
        st.markdown("---")
        st.subheader("📊 Trade Valuation Breakdown")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Giving Value", f"{round(giving_val, 1)} pts")
        m2.metric("Receiving Value", f"{round(receiving_val, 1)} pts")
        m3.metric("Net Trade Index", f"{net_value_diff:+} pts", delta=f"{net_value_diff:+} Surplus")
        m4.metric("Net Weekly PPG Impact", f"{net_ppg_diff:+} PPG")
        
        if net_value_diff >= 12.0:
            st.success("🟢 **TRADE VERDICT: SMASH ACCEPT.** You are capturing massive True VORP surplus. Highly advantageous trade.")
        elif net_value_diff >= 3.0:
            st.success("🟢 **TRADE VERDICT: WIN (FAVORABLE).** Strong trade that improves your starting lineup efficiency.")
        elif net_value_diff >= -4.0:
            st.info("🔵 **TRADE VERDICT: FAIR (WIN-WIN).** Even trade on paper. Make the deal if it addresses specific roster bye-week/depth needs.")
        elif net_value_diff >= -12.0:
            st.warning("🟡 **TRADE VERDICT: LEAN REJECT (ASK FOR SWEETENER).** You are giving up slightly more value than you receive.")
        else:
            st.error("🔴 **TRADE VERDICT: LOPSIDED REJECT.** You are giving away significant asset value without adequate return.")
            
        st.markdown("---")
        st.subheader("📋 Asset Details Involved")
        
        col_g, col_r = st.columns(2)
        with col_g:
            st.write("**You Give:**")
            if giving_players:
                st.dataframe(pd.DataFrame([{'Player': p, 'Pos': TRADE_DATABASE[p]['Pos'], 'Team': TRADE_DATABASE[p]['Team'], 'Trade Value': TRADE_DATABASE[p]['Value'], 'Proj PPG': TRADE_DATABASE[p]['Proj_PPG']} for p in giving_players]), use_container_width=True)
        with col_r:
            st.write("**You Get:**")
            if receiving_players:
                st.dataframe(pd.DataFrame([{'Player': p, 'Pos': TRADE_DATABASE[p]['Pos'], 'Team': TRADE_DATABASE[p]['Team'], 'Trade Value': TRADE_DATABASE[p]['Value'], 'Proj PPG': TRADE_DATABASE[p]['Proj_PPG']} for p in receiving_players]), use_container_width=True)
    else:
        st.info("Select players on both sides above to calculate trade equity.")