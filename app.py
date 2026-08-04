import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(
    page_title="FFB Arbitrage & Live Draft Engine", 
    page_icon="🏈", 
    layout="wide"
)

# Helper function to clean suffixes for robust matching
def clean_player_name(name):
    if not isinstance(name, str):
        return ""
    name_clean = name.strip()
    for suffix in [' III', ' II', ' Jr.', ' Sr.', ' Jr', ' Sr']:
        if name_clean.endswith(suffix):
            name_clean = name_clean[:-len(suffix)]
    return name_clean.strip().lower()

@st.cache_data
def load_data():
    excel_path = '2026-FFB-Projections-0803.xlsx'
    fp_path = 'FantasyPros_2026_Draft_OP_Rankings (3).csv'
    
    if not os.path.exists(excel_path):
        st.error(f"File {excel_path} not found in repository root!")
        return None, None, None
        
    xls = pd.ExcelFile(excel_path)
    ovr = pd.read_excel(xls, 'OVR & VORP Ranks')
    
    # Load Overall Ranks
    players = ovr[['OVERALL PLAYER', 'POS RK', 'BYE.4', 'Custom']].dropna().copy()
    players.columns = ['Player', 'Pos_RK', 'Bye', 'FPS']
    players['Pos'] = players['Pos_RK'].str.extract('([A-Z]+)')
    players['Clean_Player'] = players['Player'].apply(clean_player_name)
    
    # Load Team Projections
    team_sheets = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WSH']
    team_data = {}
    for t in team_sheets:
        try:
            df_t = pd.read_excel(xls, t)
            team_data[t] = df_t
        except Exception:
            pass
            
    fp_df = None
    if os.path.exists(fp_path):
        fp_df = pd.read_csv(fp_path)
        fp_df['Clean_FP_Name'] = fp_df['PLAYER NAME'].apply(clean_player_name)
        
    return players, team_data, fp_df

players_df, team_data, fp_df = load_data()

# Monte Carlo Engine Helper
@st.cache_data
def run_monte_carlo_sims(df, n_sims=2000):
    np.random.seed(42)
    results = []
    
    for idx, row in df.iterrows():
        mean_fps = row['FPS']
        pos = row['Pos']
        
        vol_map = {'QB': 0.15, 'RB': 0.22, 'WR': 0.25, 'TE': 0.28}
        std_dev = mean_fps * vol_map.get(pos, 0.20)
        sims = np.random.normal(mean_fps, std_dev, n_sims)
        
        results.append({
            'Player': row['Player'],
            '10th_Floor': np.percentile(sims, 10),
            '50th_Median': np.percentile(sims, 50),
            '90th_Ceiling': np.percentile(sims, 90)
        })
        
    return pd.DataFrame(results)

# Session State Initialization for Live Draft Tracking
if 'drafted_all' not in st.session_state:
    st.session_state.drafted_all = []
if 'my_roster' not in st.session_state:
    st.session_state.my_roster = []

st.title("🏈 Fantasy Football Arbitrage & Intelligence Engine")
st.caption("Custom Projections, Dynamic VORP & Live Draft Scarcity Co-Pilot")

# --- SIDEBAR: LIVE DRAFT LOG & MY SQUAD ---
with st.sidebar:
    st.header("📋 Live Draft Control Center")
    
    all_player_names = players_df['Player'].tolist() if players_df is not None else []
    
    drafted_input = st.multiselect(
        "Cross Off Drafted Players", 
        all_player_names, 
        default=st.session_state.drafted_all,
        key="drafted_selector"
    )
    st.session_state.drafted_all = drafted_input
    
    st.markdown("---")
    st.subheader("🛡️ My Drafted Squad")
    my_squad_input = st.multiselect(
        "Add Player to My Team",
        st.session_state.drafted_all,
        default=st.session_state.my_roster,
        key="my_roster_selector"
    )
    st.session_state.my_roster = my_squad_input
    
    if st.button("🔄 Reset Draft State"):
        st.session_state.drafted_all = []
        st.session_state.my_roster = []
        st.rerun()

if players_df is not None:
    tabs = st.tabs([
        "⚡ Live Draft Scarcity Monitor", 
        "🎯 True VORP Board", 
        "🌊 Volumetric Ripple Engine", 
        "⚡ QB Stacking Matrix", 
        "🕵️ Opponent Keeper Spy"
    ])

    # --- TAB 0: LIVE DRAFT SCARCITY MONITOR ---
    with tabs[0]:
        st.header("⚡ Live Draft Scarcity & Opportunity Cost Monitor")
        
        num_teams = 12
        start_qb, start_rb, start_wr, start_te, start_flex, start_op = 1, 2, 2, 0, 1, 1
        
        qb_cutoff = int(num_teams * (start_qb + start_op * 0.8))
        rb_cutoff = int(num_teams * (start_rb + start_flex * 0.4))
        wr_cutoff = int(num_teams * (start_wr + start_flex * 0.5 + (1 if start_te == 0 else 0) * 0.1))
        te_cutoff = wr_cutoff
        
        qb_base = players_df[players_df['Pos'] == 'QB'].iloc[min(qb_cutoff, len(players_df[players_df['Pos']=='QB'])-1)]['FPS']
        rb_base = players_df[players_df['Pos'] == 'RB'].iloc[min(rb_cutoff, len(players_df[players_df['Pos']=='RB'])-1)]['FPS']
        wr_base = players_df[players_df['Pos'] == 'WR'].iloc[min(wr_cutoff, len(players_df[players_df['Pos']=='WR'])-1)]['FPS']
        te_base = wr_base
        
        baselines = {'QB': qb_base, 'RB': rb_base, 'WR': wr_base, 'TE': te_base}
        
        df_calc = players_df.copy()
        df_calc['Baseline_FPS'] = df_calc['Pos'].map(baselines)
        df_calc['True_VORP'] = df_calc['FPS'] - df_calc['Baseline_FPS']
        
        # Merge FantasyPros using Clean Name
        if fp_df is not None:
            df_calc = pd.merge(df_calc, fp_df[['Clean_FP_Name', 'RK']], left_on='Clean_Player', right_on='Clean_FP_Name', how='left')
            df_calc.rename(columns={'RK': 'FP_Rank'}, inplace=True)
            df_calc.drop(columns=['Clean_FP_Name'], inplace=False)
            
        # Filter out drafted players
        df_undrafted = df_calc[~df_calc['Player'].isin(st.session_state.drafted_all)].sort_values(by='True_VORP', ascending=False).reset_index(drop=True)
        df_undrafted['Draft_Rank'] = df_undrafted.index + 1
        
        if 'FP_Rank' in df_undrafted.columns:
            df_undrafted['Rank_Surplus'] = df_undrafted['FP_Rank'] - df_undrafted['Draft_Rank']
            
        # Positional Scarcity Metrics
        st.subheader("📊 Position Supply & Tier Cliff Analysis")
        col_q, col_r, col_w, col_t = st.columns(4)
        
        scarcity_alerts = []
        pos_cols = {'QB': col_q, 'RB': col_r, 'WR': col_w, 'TE': col_t}
        
        for pos_code, col in pos_cols.items():
            pos_pool = df_undrafted[df_undrafted['Pos'] == pos_code]
            if not pos_pool.empty:
                top_player = pos_pool.iloc[0]['Player']
                top_vorp = round(pos_pool.iloc[0]['True_VORP'], 1)
                
                cliff_depth = min(5, len(pos_pool) - 1)
                next_vorp = round(pos_pool.iloc[cliff_depth]['True_VORP'], 1)
                cliff_delta = round(top_vorp - next_vorp, 1)
                
                col.metric(
                    label=f"{pos_code} Top Target: {top_player}",
                    value=f"{top_vorp} VORP",
                    delta=f"-{cliff_delta} VORP (5-pick Drop)",
                    delta_color="inverse"
                )
                
                if cliff_delta > 20.0:
                    scarcity_alerts.append(f"⚠️ **STEEP CLIFF AT {pos_code}:** Value drops **{cliff_delta} VORP** over the next 5 picks after **{top_player}**!")
                    
        if scarcity_alerts:
            for alert in scarcity_alerts:
                st.warning(alert)
        else:
            st.success("✅ Positional supply is balanced across remaining tiers.")
            
        st.markdown("---")
        st.subheader("🔥 Top 25 Best Available Players")
        st.dataframe(
            df_undrafted[['Draft_Rank', 'Player', 'Pos_RK', 'Pos', 'FPS', 'True_VORP', 'FP_Rank', 'Rank_Surplus']].head(25),
            use_container_width=True
        )

    # --- TAB 1: TRUE VORP BOARD ---
    with tabs[1]:
        st.header("1. Roster Baseline, True VORP & Monte Carlo Analytics")
        
        c1, c2, c3, c4 = st.columns(4)
        num_teams = c1.number_input("Teams in League", 8, 16, 12, key="tv_teams")
        start_qb = c2.number_input("Starting QBs", 0, 2, 1, key="tv_qb")
        start_rb = c3.number_input("Starting RBs", 1, 4, 2, key="tv_rb")
        start_wr = c4.number_input("Starting WRs", 1, 4, 2, key="tv_wr")
        
        c5, c6, c7, c8 = st.columns(4)
        start_te = c5.number_input("Starting TEs (0 = Flex Only)", 0, 2, 0, key="tv_te")
        start_flex = c6.number_input("WR/RB/TE Flex Slots", 0, 3, 1, key="tv_flex")
        start_op = c7.number_input("OP / Superflex Slots", 0, 2, 1, key="tv_op")
        rank_by = c8.selectbox("Optimize Board By", ["Expected VORP (50th)", "High Ceiling (90th %)", "Safe Floor (10th %)"], key="tv_rankby")
        
        mc_df = run_monte_carlo_sims(df_calc)
        df_tv = pd.merge(df_calc, mc_df, on='Player')
        
        if rank_by == "High Ceiling (90th %)":
            df_tv['Sort_Metric'] = df_tv['90th_Ceiling'] - df_tv['Baseline_FPS']
        elif rank_by == "Safe Floor (10th %)":
            df_tv['Sort_Metric'] = df_tv['10th_Floor'] - df_tv['Baseline_FPS']
        else:
            df_tv['Sort_Metric'] = df_tv['True_VORP']
            
        df_tv = df_tv.sort_values(by='Sort_Metric', ascending=False).reset_index(drop=True)
        df_tv['True_Rank'] = df_tv.index + 1
        
        if 'FP_Rank' in df_tv.columns:
            df_tv['Rank_Surplus'] = df_tv['FP_Rank'] - df_tv['True_Rank']
            
        st.dataframe(
            df_tv[['True_Rank', 'Player', 'Pos_RK', 'Pos', 'FPS', '10th_Floor', '90th_Ceiling', 'True_VORP', 'FP_Rank', 'Rank_Surplus']].dropna(subset=['Player']), 
            use_container_width=True
        )

    # --- TAB 2: VOLUMETRIC RIPPLE ENGINE ---
    with tabs[2]:
        st.header("2. Dynamic Volumetric Ripple Simulator")
        if team_data:
            sel_team = st.selectbox("Select Team to Simulate", list(team_data.keys()), index=5, key="vr_team")
            df_t = team_data[sel_team].copy()
            df_t['TGT SHARE'] = pd.to_numeric(df_t['TGT SHARE'], errors='coerce')
            df_t['RUSH SHARE'] = pd.to_numeric(df_t['RUSH SHARE'], errors='coerce')
            
            df_players_team = df_t[df_t['PLAYER'].notna() & (df_t['PLAYER'] != 'TEAM NUMBERS')].copy()
            
            col_vol1, col_vol2 = st.columns(2)
            team_pass_mult = col_vol1.slider(f"{sel_team} Team Pass Volume Multiplier", 0.70, 1.30, 1.00, 0.05, key="pass_mult")
            team_rush_mult = col_vol2.slider(f"{sel_team} Team Rush Volume Multiplier", 0.70, 1.30, 1.00, 0.05, key="rush_mult")
            
            sim_results = []
            for idx, row in df_players_team.head(8).iterrows():
                p_name = row['PLAYER']
                p_pos = row['POS']
                
                base_tgt_share = row['TGT SHARE'] if pd.notna(row['TGT SHARE']) else 0.0
                base_rush_share = row['RUSH SHARE'] if pd.notna(row['RUSH SHARE']) else 0.0
                
                c_p1, c_p2, c_p3 = st.columns([2, 3, 3])
                c_p1.markdown(f"**{p_name}** ({p_pos})")
                
                new_tgt_share = base_tgt_share
                new_rush_share = base_rush_share
                
                if p_pos in ['WR', 'TE', 'RB'] and base_tgt_share > 0.02:
                    new_tgt_share = c_p2.slider(f"{p_name} Target Share", 0.0, 0.40, float(round(base_tgt_share, 3)), 0.01, key=f"tgt_{p_name}")
                if p_pos in ['RB', 'QB'] and base_rush_share > 0.02:
                    new_rush_share = c_p3.slider(f"{p_name} Rush Share", 0.0, 0.85, float(round(base_rush_share, 3)), 0.02, key=f"rush_{p_name}")
                
                tgt_scale = (new_tgt_share / base_tgt_share) if base_tgt_share > 0 else 1.0
                rush_scale = (new_rush_share / base_rush_share) if base_rush_share > 0 else 1.0
                
                base_rec_pts = (row['REC']*0.5 + row['RECV YARDS']*0.1 + row['RECV TD']*6.0) if pd.notna(row['REC']) else 0.0
                base_rush_pts = (row['RUSH YARDS']*0.1 + row['RUSH TD']*6.0) if pd.notna(row['RUSH YARDS']) else 0.0
                base_pass_pts = (row['PASS YARDS']*0.04 + row['PASS TD']*6.0 + row['COMP']*0.1 - row['INT']*1.0) if pd.notna(row['PASS YARDS']) else 0.0
                
                sim_rec_pts = base_rec_pts * tgt_scale * team_pass_mult
                sim_rush_pts = base_rush_pts * rush_scale * team_rush_mult
                sim_pass_pts = base_pass_pts * team_pass_mult
                
                sim_total_fps = sim_rec_pts + sim_rush_pts + sim_pass_pts
                base_total_fps = base_rec_pts + base_rush_pts + base_pass_pts
                
                sim_results.append({
                    'PLAYER': p_name,
                    'POS': p_pos,
                    'Simulated Target Share': f"{round(new_tgt_share*100, 1)}%",
                    'Simulated Rush Share': f"{round(new_rush_share*100, 1)}%",
                    'Baseline Points': round(base_total_fps, 1),
                    'Simulated Points': round(sim_total_fps, 1),
                    'Point Shift (Δ)': round(sim_total_fps - base_total_fps, 1)
                })
            
            st.dataframe(pd.DataFrame(sim_results), use_container_width=True)

    # --- TAB 3: STACK MATRIX ---
    with tabs[3]:
        st.header("3. QB-Pass Catcher Correlation & Portfolio Stacking Matrix")
        qbs = players_df[players_df['Pos'] == 'QB']['Player'].tolist()
        sel_qb = st.selectbox("Select Starting QB", qbs[:25], index=0, key="sm_qb")
        
        qb_team = None
        qb_row = None
        for team_code, df_team in team_data.items():
            match = df_team[df_team['PLAYER'] == sel_qb]
            if not match.empty:
                qb_team = team_code
                qb_row = match.iloc[0]
                break
                
        if qb_team and qb_team in team_data:
            df_team = team_data[qb_team].copy()
            df_team['TGT SHARE'] = pd.to_numeric(df_team['TGT SHARE'], errors='coerce')
            
            df_catchers = df_team[
                (df_team['POS'].isin(['WR', 'TE', 'RB'])) & 
                (df_team['TGT SHARE'].notna()) & 
                (df_team['TGT SHARE'] > 0.02)
            ].copy()
            
            qb_fps = (qb_row['PASS YARDS']*0.04 + qb_row['PASS TD']*6.0 + qb_row['COMP']*0.1 - qb_row['INT']*1.0 + qb_row['RUSH YARDS']*0.1 + qb_row['RUSH TD']*6.0) if pd.notna(qb_row['PASS YARDS']) else 0.0
            
            stack_data = []
            for idx, c_row in df_catchers.iterrows():
                c_name = c_row['PLAYER']
                tgt_share = c_row['TGT SHARE'] if pd.notna(c_row['TGT SHARE']) else 0.0
                rec_yds = c_row['RECV YARDS'] if pd.notna(c_row['RECV YARDS']) else 0.0
                rec_tds = c_row['RECV TD'] if pd.notna(c_row['RECV TD']) else 0.0
                recs = c_row['REC'] if pd.notna(c_row['REC']) else 0.0
                
                c_fps = recs*0.5 + rec_yds*0.1 + rec_tds*6.0
                
                c_info = df_calc[df_calc['Player'] == c_name]
                c_rank = int(c_info.index[0]) + 1 if not c_info.empty else 999
                
                stack_data.append({
                    'Pass Catcher': c_name,
                    'Pos': c_row['POS'],
                    'Target Share': f"{round(tgt_share*100, 1)}%",
                    'Catcher FPS': round(c_fps, 1),
                    'Combined Stack FPS': round(qb_fps + c_fps, 1)
                })
                
            st.dataframe(pd.DataFrame(stack_data).sort_values(by='Combined Stack FPS', ascending=False), use_container_width=True)

    # --- TAB 4: OPPONENT KEEPER SPY ---
    with tabs[4]:
        st.header("4. Opponent Keeper & Trade Arbitrage Spy")
        search_player = st.selectbox("Select Player on Opponent Roster", players_df['Player'].tolist(), key="spy_player")
        
        if search_player:
            p_data = df_calc[df_calc['Player'] == search_player]
            if not p_data.empty:
                row = p_data.iloc[0]
                m1, m2, m3 = st.columns(3)
                m1.metric("Custom Baseline FPS", round(row['FPS'], 1))
                m2.metric("True VORP", round(row['True_VORP'], 1))
                m3.metric("Positional Rank", row['Pos_RK'])