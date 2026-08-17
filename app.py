import streamlit as st
import pandas as pd
import numpy as np
import os
import json

from dst_terminal import render_dst_streaming_terminal
from trade_analyzer import render_trade_analyzer

st.set_page_config(
    page_title="2026 In-Season Strategic Control Tower", 
    page_icon="🏈", 
    layout="wide"
)

# Active In-Season Modules
st.title("🏈 2026 In-Season Fantasy Strategic Terminal")
st.caption("D/ST Asymmetric Streaming Engine, Vegas Line Arbitrage & Dynamic Spreadsheet Ingestion")

tabs = st.tabs([
    "🛡️ D/ST Asymmetric Streaming Terminal",
    "📊 Weekly Projections Ingestion & Lineup Optimizer",
    "⚖️ Vegas Implied Lines & Prediction Markets",
    "🤝 Roster Distress & Trade Radar"
])

# --- TAB 1: D/ST TERMINAL ---
with tabs[0]:
    render_dst_streaming_terminal()

# --- TAB 2: PROJECTIONS INGESTION ---
with tabs[1]:
    st.header("📊 Weekly Spreadsheet Ingestion & Lineup Solver")
    st.caption("Upload your weekly projections spreadsheet directly to run lineup optimization:")
    
    uploaded_file = st.file_uploader("Upload Weekly Projections (.xlsx or .csv)", type=['xlsx', 'csv'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_proj = pd.read_csv(uploaded_file)
            else:
                df_proj = pd.read_excel(uploaded_file)
            st.success(f"✅ Successfully ingested {len(df_proj)} player projections!")
            st.dataframe(df_proj.head(20), use_container_width=True)
        except Exception as e:
            st.error(f"Error parsing file: {e}")
    else:
        st.info("💡 Drag and drop your weekly projections file above to unlock custom floor/ceiling lineup solving.")

# --- TAB 3: VEGAS MARKETS ---
with tabs[2]:
    st.header("⚖️ Vegas Implied Totals & Prop Line Arbitrage")
    st.info("Real-time implied team totals, TD equity odds, and player prop lines will populate here.")

# --- TAB 4: TRADE RADAR ---
with tabs[3]:
    st.header("🤝 Trade Distress & Leverage Radar")
    st.info("League standings, distress index, and predatory trade packages will activate after Week 1.")