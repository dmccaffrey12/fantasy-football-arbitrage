import streamlit as st
import pandas as pd
import requests

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

@st.cache_data(ttl=3600)  # Caches for 1 hour to preserve your 500 free requests/mo quota
def fetch_live_nfl_odds(api_key):
    """
    Fetches real-time Vegas Spreads & Game Totals from The-Odds-API across US sportsbooks.
    """
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
                
                # Check for DraftKings, FanDuel, or consensus lines
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
        elif response.status_code == 401:
            st.sidebar.error("❌ Invalid API Key. Check the key entered.")
        else:
            st.sidebar.warning(f"⚠️ API Status {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"Error connecting to odds API: {e}")
    return None