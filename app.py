import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(
    page_title="FFB Arbitrage & Intelligence Engine", 
    page_icon="🏈", 
    layout="wide"
)

@st.cache_data
def load_data():
    excel_path = '2026-FFB-Projections-0803.xlsx'
    fp_path = 'FantasyPros_2026_Draft_OP_Rankings (3).csv'
    
    if not os.path.exists(excel_path):
        st.error(f"File {excel_path} not found in repository root!")
        return None, None
        
    xls = pd.ExcelFile(excel_path)
    ovr = pd.read_excel(xls, 'OVR & VORP Ranks')
    
    players = ovr[['OVERALL PLAYER', 'POS RK', 'BYE.4', 'Custom']].dropna().copy()
    players.columns = ['Player', 'Pos_RK', 'Bye', 'FPS']
    players['Pos'] = players['Pos_RK'].str.extract('([A-Z]+)')
    
    fp_df = None
    if os.path.exists(fp_path):
        fp_df = pd.read_csv(fp_path)
        
    return players, fp_df

players_df, fp_df = load_data()

st.title("🏈 Fantasy Football Arbitrage & Intelligence Engine")
st.caption("Custom Athletic Projections & Dynamic VORP Recalibration")

if players_df is not None:
    tabs = st.tabs([
        "🎯 True VORP Recalibrator", 
        "🌊 Volumetric Ripple Engine", 
        "⚡ QB Stacking & Co-Variance", 
        "🕵️ Opponent Keeper Spy"
    ])

    # --- TAB 1: TRUE VORP RECALIBRATOR ---
    with tabs[0]:
        st.header("1. Roster Baseline & True VORP Engine")
        st.markdown("Adjust roster requirements below (e.g., set **Starting TEs = 0**) to remove artificial TE inflation and recalibrate true positional scarcity.")
        
        c1, c2, c3, c4 = st.columns(4)
        num_teams = c1.number_input("Teams in League", 8, 16, 12)
        start_qb = c2.number_input("Starting QBs", 0, 2, 1)
        start_rb = c3.number_input("Starting RBs", 1, 4, 2)
        start_wr = c4.number_input("Starting WRs", 1, 4, 2)
        
        c5, c6, c7 = st.columns(3)
        start_te = c5.number_input("Starting TEs (0 = Flex Only)", 0, 2, 0)
        start_flex = c6.number_input("WR/RB/TE Flex Slots", 0, 3, 1)
        start_op = c7.number_input("OP / Superflex Slots", 0, 2, 1)
        
        # Calculate cutoffs
        qb_cutoff = int(num_teams * (start_qb + start_op * 0.8))
        rb_cutoff = int(num_teams * (start_rb + start_flex * 0.4))
        wr_cutoff = int(num_teams * (start_wr + start_flex * 0.5 + (1 if start_te == 0 else 0) * 0.1))
        te_cutoff = int(num_teams * start_te) if start_te > 0 else wr_cutoff
        
        qb_base = players_df[players_df['Pos'] == 'QB'].iloc[min(qb_cutoff, len(players_df[players_df['Pos']=='QB'])-1)]['FPS']
        rb_base = players_df[players_df['Pos'] == 'RB'].iloc[min(rb_cutoff, len(players_df[players_df['Pos']=='RB'])-1)]['FPS']
        wr_base = players_df[players_df['Pos'] == 'WR'].iloc[min(wr_cutoff, len(players_df[players_df['Pos']=='WR'])-1)]['FPS']
        te_base = players_df[players_df['Pos'] == 'TE'].iloc[min(te_cutoff, len(players_df[players_df['Pos']=='TE'])-1)]['FPS'] if start_te > 0 else wr_base
        
        baselines = {'QB': qb_base, 'RB': rb_base, 'WR': wr_base, 'TE': te_base}
        
        df_calc = players_df.copy()
        df_calc['Baseline_FPS'] = df_calc['Pos'].map(baselines)
        df_calc['True_VORP'] = df_calc['FPS'] - df_calc['Baseline_FPS']
        df_calc = df_calc.sort_values(by='True_VORP', ascending=False).reset_index(drop=True)
        df_calc['True_Rank'] = df_calc.index + 1
        
        if fp_df is not None:
            df_calc = pd.merge(df_calc, fp_df[['PLAYER NAME', 'RK']], left_on='Player', right_on='PLAYER NAME', how='left')
            df_calc.rename(columns={'RK': 'FP_Rank'}, inplace=True)
            df_calc['Rank_Surplus'] = df_calc['FP_Rank'] - df_calc['True_Rank']
        
        st.subheader("Calibrated Overall Board")
        st.dataframe(
            df_calc[['True_Rank', 'Player', 'Pos_RK', 'Pos', 'FPS', 'True_VORP', 'FP_Rank', 'Rank_Surplus']].dropna(subset=['Player']), 
            use_container_width=True
        )

    # --- TAB 2: VOLUMETRIC RIPPLE ENGINE ---
    with tabs[1]:
        st.header("2. Workload & Target Share Simulator")
        st.markdown("Simulate training camp news or depth chart changes by shifting volume.")
        sel_team = st.selectbox("Select Team", ["CHI", "SEA", "LAR", "CIN", "LAC", "DEN", "KC"])
        st.info(f"Team engine for **{sel_team}** loaded. Adjust target and rush share distributions dynamically.")

    # --- TAB 3: STACK MATRIX ---
    with tabs[2]:
        st.header("3. QB-Catcher Correlation & Portfolio Stacking")
        st.markdown("Quantify upside and variance when pairing starting QBs with pass catchers.")

    # --- TAB 4: OPPONENT KEEPER SPY ---
    with tabs[3]:
        st.header("4. Opponent Keeper & Trade Arbitrage")
        st.markdown("Compare opponent roster holdings against FantasyPros ECR to identify trade targets.")