import streamlit as st
import pandas as pd
import requests

# Live Free Market Data Handler
# Uses The-Odds-API (free key) or Polymarket Public Gamma API

@st.cache_data(ttl=3600)  # Caches for 1 hour to preserve free API quota
def fetch_live_nfl_odds(api_key=None):
    """
    Fetches real-time Vegas Spreads & Game Totals across US sportsbooks.
    Free tier allows 500 requests/month.
    """
    if not api_key:
        return None
        
    url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
    params = {
        'apiKey': api_key,
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
                home = event.get('home_team')
                away = event.get('away_team')
                commence = event.get('commence_time')
                
                # Extract DraftKings or consensus market
                spread = 0.0
                total = 43.0
                for bookmaker in event.get('bookmakers', []):
                    if bookmaker['key'] in ['draftkings', 'fanduel']:
                        for m in bookmaker.get('markets', []):
                            if m['key'] == 'spreads':
                                for outcome in m['outcomes']:
                                    if outcome['name'] == home:
                                        spread = outcome.get('point', 0.0)
                            elif m['key'] == 'totals':
                                total = m['outcomes'][0].get('point', 43.0)
                        break
                        
                games.append({
                    'Home_Team': home,
                    'Away_Team': away,
                    'Home_Spread': spread,
                    'Game_Total': total,
                    'Home_Implied_Pts': round((total / 2.0) - (spread / 2.0), 1),
                    'Away_Implied_Pts': round((total / 2.0) + (spread / 2.0), 1),
                    'Kickoff': commence
                })
            return pd.DataFrame(games)
    except Exception as e:
        st.error(f"Error connecting to live market feed: {e}")
    return None

@st.cache_data(ttl=1800)
def fetch_polymarket_sentiment(slug="nfl"):
    """
    Pulls open-access prediction market liquidity and win probabilities from Polymarket.
    Requires no API keys.
    """
    url = f"https://gamma-api.polymarket.com/events?slug={slug}&limit=20"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None