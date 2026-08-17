import streamlit as st
import pandas as pd
import numpy as np

from dst_terminal import render_dst_streaming_terminal
from lineup_optimizer import render_lineup_optimizer
from market_api import fetch_live_nfl_odds

st.set_page_config(
    page_title="2026 In-Season Strategic Control Tower", 
    page_icon="🏈", 
    layout="wide"
)

# --- SIDEBAR: LIVE API SETTINGS ---
with st.sidebar:
    st.header("🔑 Live Market API Settings")
    
    api_key_input = st.text_input(
        "The-Odds-API Key", 
        value=st.session_state.get('the_odds_api_key', ''),
        type="password",
        placeholder="Paste your free API key here...",
        help="Get your free key with 500 requests/month at the-odds-api.com"
    )
    
    if api_key_input:
        st.session_state.the_odds_api_key = api_key_input
        st.success("✅ API Key Loaded!")
        
    st.markdown("---")
    st.caption("Live Roster Status: Dak, Goff, Chase Brown, Hampton, Bucky, London, DJ Moore, JAX D/ST")

st.title("🏈 2026 In-Season Fantasy Strategic Terminal")
st.caption("D/ST Asymmetric Streaming Engine, Live Vegas Line Arbitrage & Dynamic Spreadsheet Ingestion")

tabs = st.tabs([
    "🛡️ D/ST Asymmetric Streaming Terminal",
    "📊 Weekly Projections & Lineup Solver",
    "⚖️ Live Vegas Spreads & Implied Totals",
    "🤝 Roster Distress & Trade Radar"
])

# --- TAB 1: D/ST TERMINAL ---
with tabs[0]:
    render_dst_streaming_terminal()

# --- TAB 2: PROJECTIONS & LINEUP SOLVER ---
with tabs[1]:
    render_lineup_optimizer()

# --- TAB 3: LIVE VEGAS TOTALS & SPREADS ---
with tabs[2]:
    st.header("⚖️ Live Vegas Spreads & Implied Team Totals")
    st.caption("Real-time betting market data directly from US Sportsbooks (DraftKings, FanDuel):")
    
    active_key = st.session_state.get('the_odds_api_key', '')
    if active_key:
        with st.spinner("Fetching live NFL odds..."):
            df_odds = fetch_live_nfl_odds(active_key)
            
        if df_odds is not None and not df_odds.empty:
            st.dataframe(
                df_odds[['Away_Team', 'Home_Team', 'Spread', 'Game_Total', 'Away_Implied_Pts', 'Home_Implied_Pts', 'Kickoff']],
                use_container_width=True
            )
            
            st.markdown("---")
            st.subheader("🔥 High-Scoring Shootout Watch (Game Totals $\ge$ 47.5)")
            shootouts = df_odds[df_odds['Game_Total'] >= 47.5]
            if not shootouts.empty:
                for idx, row in shootouts.iterrows():
                    st.info(f"⚡ **{row['Away_Team']} @ {row['Home_Team']}** | Total: **{row['Game_Total']}** | Implied: {row['Away_Code']} ({row['Away_Implied_Pts']}) vs {row['Home_Code']} ({row['Home_Implied_Pts']})")
            else:
                st.write("No extreme high-total shootouts currently flagged.")
        else:
            st.info("No active NFL game lines returned for this week yet.")
    else:
        st.warning("⚠️ **No API Key Found.** Enter your free API key in the sidebar on the left to unlock live odds.")

# --- TAB 4: TRADE RADAR ---
with tabs[3]:
    st.header("🤝 Trade Distress & Leverage Radar")
    st.info("Rival roster distress indicators and buy-low targets will activate after Week 1.")