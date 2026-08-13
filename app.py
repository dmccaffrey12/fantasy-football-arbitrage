import streamlit as st
import pandas as pd
import numpy as np
import os
import json

# Import standalone trade analyzer module
from trade_analyzer import render_trade_analyzer

st.set_page_config(
    page_title="FFB Arbitrage & Live Draft Engine", 
    page_icon="🏈", 
    layout="wide"
)

STATE_FILE = 'draft_state.json'

# LOCKED-IN LEAGUE KEEPERS MAPPED TO EXACT OVERALL PICK NUMBERS
KEEPER_PICK_MAPPING = {
    3: "Jahmyr Gibbs",           # Team 3 (Torta Pounder)
    5: "Ja'Marr Chase",          # Team 5 (F'ready set go)
    7: "Bijan Robinson",         # Team 7 (Patronessy)
    8: "Puka Nacua",             # Team 8 (Saquon Deez Nutz)
    16: "Justin Jefferson",      # Team 9 (Collins outta here nico)
    18: "Jonathan Taylor",       # Team 7 (Patronessy)
    22: "Jaxon Smith-Njigba",    # Team 3 (Torta Pounder)
    23: "Christian McCaffrey",   # Team 2 (Bring me My Flowers)
    24: "Amon-Ra St. Brown",     # Team 1 (SSG John 'Four Leaf' Tayback)
    25: "James Cook",            # Team 1 (SSG John 'Four Leaf' Tayback)
    28: "Ashton Jeanty",         # Team 4 (Last Place Chronicles)
    29: "De'Von Achane",         # Team 5 (F'ready set go)
    39: "Omarion Hampton",       # Team 10 (MY TEAM)
    41: "Saquon Barkley",        # Team 8 (Saquon Deez Nutz)
    47: "Brock Bowers",          # Team 2 (Bring me My Flowers)
    54: "Derrick Henry",         # Team 6 (Team Gregory)
    61: "Davante Adams",         # Team 12 (Bush Wookies)
    62: "Javonte Williams",      # Team 11 (Jimmy's scary team)
    67: "Terry McLaurin",        # Team 6 (Team Gregory)
    76: "TreVeyon Henderson",    # Team 4 (Last Place Chronicles)
    81: "Tyler Warren",          # Team 9 (Collins outta here nico)
    107: "Michael Pittman"       # Team 11 (Jimmy's scary team)
}

DEFAULT_KEEPERS = list(KEEPER_PICK_MAPPING.values())
DEFAULT_MY_SQUAD = ["Omarion Hampton"]

# 12-TEAM SNAKE DRAFT PICK MATRIX MAPPING (180 PICKS)
PICK_TO_TEAM_MAP = {}
for rd in range(1, 16):
    for p in range(1, 13):
        overall = (rd - 1) * 12 + p
        if rd % 2 == 1:
            team_num = p
        else:
            team_num = 13 - p
        PICK_TO_TEAM_MAP[overall] = team_num

# Helper function to save draft state to disk
def save_draft_state():
    state_data = {
        'drafted_all': st.session_state.drafted_all,
        'my_roster': st.session_state.my_roster,
        'my_watchlist': st.session_state.my_watchlist
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state_data, f)

# Helper function to load draft state from disk
def load_draft_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {'drafted_all': DEFAULT_KEEPERS, 'my_roster': DEFAULT_MY_SQUAD, 'my_watchlist': []}

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
def calculate_player_bonuses(team_data):
    """Simulates milestone game and long TD bonuses across 17-game schedules for all team sheets."""
    bonuses = {}
    np.random.seed(42)
    games = 17.0
    
    for team_code, df_t in team_data.items():
        if df_t is None or df_t.empty:
            continue
        for idx, row in df_t.iterrows():
            p_name = row.get('PLAYER')
            p_pos = row.get('POS')
            if pd.isna(p_name) or p_name == 'TEAM NUMBERS' or not isinstance(p_name, str):
                continue
                
            pass_yds = float(row['PASS YARDS']) if pd.notna(row.get('PASS YARDS')) and isinstance(row.get('PASS YARDS'), (int, float)) else 0.0
            pass_td = float(row['PASS TD']) if pd.notna(row.get('PASS TD')) and isinstance(row.get('PASS TD'), (int, float)) else 0.0
            rush_yds = float(row['RUSH YARDS']) if pd.notna(row.get('RUSH YARDS')) and isinstance(row.get('RUSH YARDS'), (int, float)) else 0.0
            rush_td = float(row['RUSH TD']) if pd.notna(row.get('RUSH TD')) and isinstance(row.get('RUSH TD'), (int, float)) else 0.0
            rec_yds = float(row['RECV YARDS']) if pd.notna(row.get('RECV YARDS')) and isinstance(row.get('RECV YARDS'), (int, float)) else 0.0
            rec_td = float(row['RECV TD']) if pd.notna(row.get('RECV TD')) and isinstance(row.get('RECV TD'), (int, float)) else 0.0
            
            p_bonus = 0.0
            if pass_yds > 0:
                avg_p_yds = pass_yds / games
                sims = np.random.normal(avg_p_yds, 60.0, (400, 17))
                b300 = np.mean(np.sum((sims >= 300) & (sims < 400), axis=1)) * 2.0
                b400 = np.mean(np.sum(sims >= 400, axis=1)) * 3.0
                p_bonus = b300 + b400
                
            r_bonus = 0.0
            if rush_yds > 0:
                avg_r_yds = rush_yds / games
                sims = np.random.normal(avg_r_yds, max(12.0, avg_r_yds * 0.4), (400, 17))
                b100 = np.mean(np.sum((sims >= 100) & (sims < 200), axis=1)) * 1.0
                b200 = np.mean(np.sum(sims >= 200, axis=1)) * 2.0
                r_bonus = b100 + b200
                
            c_bonus = 0.0
            if rec_yds > 0:
                avg_c_yds = rec_yds / games
                sims = np.random.normal(avg_c_yds, max(12.0, avg_c_yds * 0.45), (400, 17))
                b100c = np.mean(np.sum((sims >= 100) & (sims < 200), axis=1)) * 1.0
                b200c = np.mean(np.sum(sims >= 200, axis=1)) * 2.0
                c_bonus = b100c + b200c
                
            td_p_b = pass_td * (0.10 * 1.0 + 0.06 * 4.0)
            td_r_b = rush_td * (0.08 * 1.0 + 0.04 * 2.0)
            td_c_b = rec_td * (0.12 * 1.0 + 0.08 * 2.0)
            
            total_bonus = p_bonus + r_bonus + c_bonus + td_p_b + td_r_b + td_c_b
            c_name = clean_player_name(p_name)
            bonuses[c_name] = round(total_bonus, 2)
            
    return bonuses

@st.cache_data
def load_data():
    excel_path = '2026-FFB-Projections-0812.xlsx'
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

# Initialize Session State from Disk on First Load
saved_state = load_draft_state()
if 'drafted_all' not in st.session_state:
    st.session_state.drafted_all = saved_state.get('drafted_all', DEFAULT_KEEPERS)
if 'my_roster' not in st.session_state:
    st.session_state.my_roster = saved_state.get('my_roster', DEFAULT_MY_SQUAD)
if 'my_watchlist' not in st.session_state:
    st.session_state.my_watchlist = saved_state.get('my_watchlist', [])

st.title("🏈 Fantasy Football Arbitrage & Intelligence Engine")
st.caption("Precision Pick-to-Team Mapping, Auto-Sniper Engine & Dynamic VORP Co-Pilot")

# Global Master Processing for Base Rankings
if players_df is not None:
    df_calc = players_df.copy()
    
    # Calculate Bonuses
    if team_data:
        bonus_dict = calculate_player_bonuses(team_data)
        df_calc['Bonus_PTS'] = df_calc['Clean_Player'].map(bonus_dict).fillna(0.0)
        df_calc['FPS'] = df_calc['FPS'] + df_calc['Bonus_PTS']
    else:
        df_calc['Bonus_PTS'] = 0.0

    num_teams = 12
    start_qb, start_rb, start_wr, start_te, start_flex, start_op = 1, 2, 2, 0, 1, 1
    
    qb_cutoff = int(num_teams * (start_qb + start_op * 0.8))
    rb_cutoff = int(num_teams * (start_rb + start_flex * 0.4))
    wr_cutoff = int(num_teams * (start_wr + start_flex * 0.5 + (1 if start_te == 0 else 0) * 0.1))
    te_cutoff = wr_cutoff
    
    qb_base = df_calc[df_calc['Pos'] == 'QB'].iloc[min(qb_cutoff, len(df_calc[df_calc['Pos']=='QB'])-1)]['FPS']
    rb_base = df_calc[df_calc['Pos'] == 'RB'].iloc[min(rb_cutoff, len(df_calc[df_calc['Pos']=='RB'])-1)]['FPS']
    wr_base = df_calc[df_calc['Pos'] == 'WR'].iloc[min(wr_cutoff, len(df_calc[df_calc['Pos']=='WR'])-1)]['FPS']
    te_base = wr_base
    
    baselines = {'QB': qb_base, 'RB': rb_base, 'WR': wr_base, 'TE': te_base}
    
    df_calc['Baseline_FPS'] = df_calc['Pos'].map(baselines)
    df_calc['True_VORP'] = df_calc['FPS'] - df_calc['Baseline_FPS']
    
    if fp_df is not None:
        df_calc = pd.merge(df_calc, fp_df[['Clean_FP_Name', 'RK']], left_on='Clean_Player', right_on='Clean_FP_Name', how='left')
        df_calc.rename(columns={'RK': 'FP_Rank'}, inplace=True)
        if 'Clean_FP_Name' in df_calc.columns:
            df_calc.drop(columns=['Clean_FP_Name'], inplace=True)
            
    df_calc = df_calc.sort_values(by='True_VORP', ascending=False).reset_index(drop=True)
    df_calc['True_Rank'] = df_calc.index + 1
    df_calc['Rank_Surplus'] = df_calc['FP_Rank'] - df_calc['True_Rank']

# BUILD ACCURATE LEAGUE TEAM ROSTER MATRIX
team_rosters = {i: [] for i in range(1, 13)}

# Assign keepers directly by their exact forfeited pick number
for p_num, p_name in KEEPER_PICK_MAPPING.items():
    assigned_team = PICK_TO_TEAM_MAP.get(p_num, 1)
    team_rosters[assigned_team].append(p_name)

# Assign live draft selections made during the draft
live_drafted = [p for p in st.session_state.drafted_all if p not in DEFAULT_KEEPERS]
for idx, p_name in enumerate(live_drafted):
    live_pick_num = idx + 1
    assigned_team = PICK_TO_TEAM_MAP.get(live_pick_num, 10)
    team_rosters[assigned_team].append(p_name)

# --- SIDEBAR: LIVE DRAFT LOG, WATCHLIST & CONTROLS ---
with st.sidebar:
    st.header("📋 Live Draft Control Center")
    
    all_player_names = players_df['Player'].tolist() if players_df is not None else []
    
    # Live Draft Pick Counter Fix
    live_selections = [p for p in st.session_state.drafted_all if p not in DEFAULT_KEEPERS]
    live_pick_num = len(live_selections) + 1
    current_round_num = ((live_pick_num - 1) // 12) + 1
    on_clock_team = PICK_TO_TEAM_MAP.get(live_pick_num, 10)
    
    m_side1, m_side2 = st.columns(2)
    m_side1.metric("Live Draft Pick", f"#{live_pick_num}")
    m_side2.metric("On The Clock", f"Team #{on_clock_team}" if on_clock_team != 10 else "⭐ YOU (#10)")
    
    st.markdown("---")
    st.subheader("📌 On-the-Clock Target Watchlist")
    
    active_watchlist_options = [p for p in all_player_names if p not in st.session_state.drafted_all]
    watchlist_input = st.multiselect(
        "Bookmark Targets for Next Pick",
        active_watchlist_options,
        default=[p for p in st.session_state.my_watchlist if p in active_watchlist_options],
        key="watchlist_selector"
    )
    if watchlist_input != st.session_state.my_watchlist:
        st.session_state.my_watchlist = watchlist_input
        save_draft_state()
        
    st.markdown("---")
    
    # Cross off drafted players across the league
    drafted_input = st.multiselect(
        "Cross Off Drafted Players / Keepers", 
        all_player_names, 
        default=[p for p in st.session_state.drafted_all if p in all_player_names],
        key="drafted_selector"
    )
    if drafted_input != st.session_state.drafted_all:
        st.session_state.drafted_all = drafted_input
        save_draft_state()
    
    st.markdown("---")
    st.subheader("🛡️ My Drafted Squad")
    
    my_squad_input = st.multiselect(
        "Add Player to My Team",
        all_player_names,
        default=[p for p in st.session_state.my_roster if p in all_player_names],
        key="my_roster_selector"
    )
    if my_squad_input != st.session_state.my_roster:
        st.session_state.my_roster = my_squad_input
        save_draft_state()
        
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("💾 Save State"):
        save_draft_state()
        st.success("Saved to disk!")
        
    if col_btn2.button("🔄 Reset Keepers"):
        st.session_state.drafted_all = DEFAULT_KEEPERS
        st.session_state.my_roster = DEFAULT_MY_SQUAD
        st.session_state.my_watchlist = []
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        st.rerun()

if players_df is not None:
    tabs = st.tabs([
        "⚡ Live Draft Scarcity Monitor", 
        "🎯 True VORP Board", 
        "🌊 Volumetric Ripple Engine", 
        "⚡ QB Stacking Matrix", 
        "🤝 Preseason Trade Spy"
    ])

    # --- TAB 0: LIVE DRAFT SCARCITY MONITOR & AUTO-SNIPER SPY ---
    with tabs[0]:
        st.header("⚡ Live Draft Scarcity & Auto-Sniper Intelligence Board")
        
        # Filter out drafted players & keepers
        df_undrafted = df_calc[~df_calc['Player'].isin(st.session_state.drafted_all)].sort_values(by='True_VORP', ascending=False).reset_index(drop=True)
        df_undrafted['Effective_Unkept_Rank'] = df_undrafted.index + 1
        
        if 'FP_Rank' in df_undrafted.columns:
            df_undrafted['Rank_Surplus'] = df_undrafted['FP_Rank'] - df_undrafted['Effective_Unkept_Rank']
            
        # Positional Scarcity Metrics
        st.subheader("📊 Position Supply & Tier Cliff Analysis (Unkept Pool)")
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
            st.success("✅ Positional supply is balanced across remaining unkept tiers.")
            
        st.markdown("---")
        
        # AUTO-CALCULATE TURN MANAGERS & POSITIONAL DEMAND
        scheduled_picks = [10, 15, 34, 39, 58, 63, 82, 87, 106, 111, 130, 135, 154, 159, 178]
        next_my_pick = next((p for p in scheduled_picks if p >= live_pick_num), scheduled_picks[-1])
        
        turn_picks = list(range(live_pick_num, next_my_pick))
        turn_teams = list(set([PICK_TO_TEAM_MAP.get(p, 1) for p in turn_picks if PICK_TO_TEAM_MAP.get(p, 1) != 10]))
        
        turn_qbs_count, turn_rbs_count, turn_wrs_count, turn_tes_count = 0, 0, 0, 0
        for t_id in turn_teams:
            t_players = team_rosters[t_id]
            df_t_roster = df_calc[df_calc['Player'].isin(t_players)]
            turn_qbs_count += len(df_t_roster[df_t_roster['Pos'] == 'QB'])
            turn_rbs_count += len(df_t_roster[df_t_roster['Pos'] == 'RB'])
            turn_wrs_count += len(df_t_roster[df_t_roster['Pos'] == 'WR'])
            turn_tes_count += len(df_t_roster[df_t_roster['Pos'] == 'TE'])
            
        st.subheader("⚖️ Auto-Sniper Engine (Automated Need-Weighted Turn Spy)")
        st.caption(f"🕵️ **Turn Intelligence (Picks #{live_pick_num} to #{next_my_pick}):** Evaluating Rival Teams **{', '.join([f'Team {t}' for t in turn_teams]) if turn_teams else 'None (You are On the Clock!)'}**")
        
        calc_col1, calc_col2 = st.columns(2)
        target_player_sel = calc_col1.selectbox("Target Arbitrage Player", df_undrafted['Player'].tolist()[:300], index=min(0, len(df_undrafted)-1))
        next_pick_num = calc_col2.number_input("Target Pick Slot", min_value=1, max_value=200, value=next_my_pick, step=1)
        
        if target_player_sel:
            p_data = df_undrafted[df_undrafted['Player'] == target_player_sel].iloc[0]
            target_pos = p_data['Pos']
            target_fp_rank = p_data['FP_Rank'] if pd.notna(p_data['FP_Rank']) else p_data['Effective_Unkept_Rank']
            target_true_rank = p_data['Effective_Unkept_Rank']
            target_vorp = p_data['True_VORP']
            
            fp_buffer = target_fp_rank - next_pick_num
            
            if fp_buffer >= 10:
                survival_prob = min(95, 75 + int(fp_buffer * 1.5))
            elif fp_buffer >= 0:
                survival_prob = max(40, 50 + int(fp_buffer * 2.5))
            else:
                survival_prob = max(5, 40 + int(fp_buffer * 3.0))
                
            blockade_active = False
            if target_pos == 'QB' and (turn_qbs_count >= len(turn_teams) * 1.0 or len(turn_teams) == 0):
                blockade_active = True
            elif target_pos == 'RB' and turn_rbs_count >= len(turn_teams) * 2.0:
                blockade_active = True
            elif target_pos == 'WR' and turn_wrs_count >= len(turn_teams) * 2.5:
                blockade_active = True
                
            if blockade_active:
                survival_prob = min(98, survival_prob + 30)
                st.info(f"🛡️ **AUTO-BLOCKADE ACTIVE:** Rival Turn Managers have saturated **{target_pos}** demand ({turn_qbs_count if target_pos=='QB' else turn_rbs_count} drafted). Survival odds boosted to **{survival_prob}%**!")
                
            safety_net_pool = df_undrafted[
                (df_undrafted['Player'] != target_player_sel) & 
                (df_undrafted['True_VORP'] >= target_vorp - 20.0) &
                (df_undrafted['FP_Rank'] >= next_pick_num - 8)
            ]
            safety_count = len(safety_net_pool)
            
            m_s1, m_s2, m_s3, m_s4 = st.columns(4)
            m_s1.metric("Target FP ECR Rank", int(target_fp_rank) if pd.notna(target_fp_rank) else "N/A")
            m_s2.metric("Effective Unkept Rank", int(target_true_rank))
            m_s3.metric("Auto-Snipe Survival Odds", f"{survival_prob}%")
            m_s4.metric("Safety Net Alternatives", f"{safety_count} Players")
            
            if survival_prob >= 75 and safety_count >= 2:
                st.success(f"🟢 **RECOMMENDATION: SAFE TO WAIT.** {target_player_sel} has high survival odds ({survival_prob}%) to reach Pick {next_pick_num}. Harvest surplus!")
            elif survival_prob >= 60 and safety_count >= 1:
                st.info(f"🔵 **RECOMMENDATION: LOW/MODERATE RISK.** {target_player_sel} has {survival_prob}% survival odds to reach Pick {next_pick_num}. Reasonable candidate to let ride.")
            elif survival_prob >= 40 or safety_count >= 1:
                st.warning(f"⚠️ **RECOMMENDATION: HIGH SNIPE RISK (<60%).** {target_player_sel} has only **{survival_prob}%** survival odds to reach Pick {next_pick_num}. Backup options: {', '.join(safety_net_pool['Player'].tolist()[:3]) if safety_count > 0 else 'None'}.")
            else:
                st.error(f"🔴 **RECOMMENDATION: DRAFT NOW.** {target_player_sel} is at critical risk of being sniped before Pick {next_pick_num} (Survival: {survival_prob}%). Pull the trigger now.")

        # EXPANDER: LIVE ACCURATE LEAGUE ROSTER & NEED DASHBOARD
        with st.expander("🕵️ Live Opponent Roster & Need Dashboard (Teams 1 - 12)", expanded=False):
            team_cols = st.columns(4)
            for t_idx in range(1, 13):
                col = team_cols[(t_idx - 1) % 4]
                t_p_names = team_rosters[t_idx]
                df_t_ros = df_calc[df_calc['Player'].isin(t_p_names)]
                
                qb_c = len(df_t_ros[df_t_ros['Pos'] == 'QB'])
                rb_c = len(df_t_ros[df_t_ros['Pos'] == 'RB'])
                wr_c = len(df_t_ros[df_t_ros['Pos'] == 'WR'])
                te_c = len(df_t_ros[df_t_ros['Pos'] == 'TE'])
                
                col.markdown(f"**Team #{t_idx}{' (YOU)' if t_idx==10 else ''}**")
                col.caption(f"QBs: {qb_c} | RBs: {rb_c} | WRs: {wr_c} | TEs: {te_c}")
                col.caption(f"Keepers/Roster: {', '.join(t_p_names) if t_p_names else 'None'}")
                col.markdown("---")

        st.markdown("---")
        st.subheader("🔥 Available Unkept Execution Table")
        
        pos_filter = st.radio("Filter By Position Tier", ["ALL", "QB", "RB", "WR", "TE"], horizontal=True, key="pos_filter_radio")
        
        df_filtered_board = df_undrafted.copy()
        if pos_filter != "ALL":
            df_filtered_board = df_filtered_board[df_filtered_board['Pos'] == pos_filter].reset_index(drop=True)
            
        top_15_board = df_filtered_board.head(15)
        
        # Display Quick Execution Table with Inline Buttons
        header_cols = st.columns([1, 3, 1, 1, 1.5, 1.5, 1.5, 1.5])
        header_cols[0].markdown("**Unkept Rk**")
        header_cols[1].markdown("**Player**")
        header_cols[2].markdown("**Pos**")
        header_cols[3].markdown("**FPS**")
        header_cols[4].markdown("**True VORP**")
        header_cols[5].markdown("**FP Cost**")
        header_cols[6].markdown("**Draft Me**")
        header_cols[7].markdown("**Mark Taken**")
        
        st.markdown("---")
        
        for idx, row in top_15_board.iterrows():
            p_name = row['Player']
            cols = st.columns([1, 3, 1, 1, 1.5, 1.5, 1.5, 1.5])
            
            cols[0].write(f"#{row['Effective_Unkept_Rank']}")
            cols[1].write(f"**{p_name}**")
            cols[2].write(row['Pos_RK'])
            cols[3].write(f"{round(row['FPS'], 1)}")
            cols[4].write(f"**+{round(row['True_VORP'], 1)}**")
            cols[5].write(f"#{int(row['FP_Rank'])}" if pd.notna(row['FP_Rank']) else "N/A")
            
            # Button 1: Draft Me
            if cols[6].button("🟢 My Pick", key=f"btn_my_{p_name}_{idx}"):
                st.session_state.drafted_all.append(p_name)
                st.session_state.my_roster.append(p_name)
                save_draft_state()
                st.rerun()
                
            # Button 2: Cross Off
            if cols[7].button("🔴 Taken", key=f"btn_off_{p_name}_{idx}"):
                st.session_state.drafted_all.append(p_name)
                save_draft_state()
                st.rerun()

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
            df_tv[['True_Rank', 'Player', 'Pos_RK', 'Pos', 'FPS', 'Bonus_PTS', '10th_Floor', '90th_Ceiling', 'True_VORP', 'FP_Rank', 'Rank_Surplus']].dropna(subset=['Player']), 
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
                
                base_rec_pts = (row['REC']*1.0 + row['RECV YARDS']*0.1 + row['RECV TD']*6.0) if pd.notna(row['REC']) else 0.0
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
        sel_qb = st.selectbox("Select Starting QB", qbs, index=0, key="sm_qb")
        
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
            
            st.markdown(f"### 🎯 Team Stack Dashboard: **{sel_qb} ({qb_team})**")
            m1, m2, m3 = st.columns(3)
            m1.metric("QB Projected Points", round(qb_fps, 1))
            m2.metric("Projected Pass Attempts", int(qb_row['PASS ATT']) if pd.notna(qb_row['PASS ATT']) else "N/A")
            m3.metric("Projected Pass TDs", round(qb_row['PASS TD'], 1) if pd.notna(qb_row['PASS TD']) else "N/A")
            
            st.markdown("---")
            st.subheader(f"Pass Catcher Portfolio Options for {sel_qb}")
            
            stack_data = []
            for idx, c_row in df_catchers.iterrows():
                c_name = c_row['PLAYER']
                tgt_share = c_row['TGT SHARE'] if pd.notna(c_row['TGT SHARE']) else 0.0
                rec_yds = c_row['RECV YARDS'] if pd.notna(c_row['RECV YARDS']) else 0.0
                rec_tds = c_row['RECV TD'] if pd.notna(c_row['RECV TD']) else 0.0
                recs = c_row['REC'] if pd.notna(c_row['REC']) else 0.0
                
                c_fps = recs*1.0 + rec_yds*0.1 + rec_tds*6.0
                stack_total = qb_fps + c_fps
                
                c_info = df_calc[df_calc['Player'] == c_name]
                c_rank = int(c_info['True_Rank'].values[0]) if not c_info.empty and 'True_Rank' in c_info.columns else 999
                fp_rank = int(c_info['FP_Rank'].values[0]) if not c_info.empty and 'FP_Rank' in c_info.columns and pd.notna(c_info['FP_Rank'].values[0]) else 999
                
                surplus_val = (fp_rank - c_rank) if fp_rank < 999 else "N/A"
                
                stack_data.append({
                    'Pass Catcher': c_name,
                    'Pos': c_row['POS'],
                    'Target Share': f"{round(tgt_share*100, 1)}%",
                    'Catcher FPS': round(c_fps, 1),
                    'Combined Stack FPS': round(stack_total, 1),
                    'Custom True Rank': c_rank if c_rank < 999 else "N/A",
                    'FP Cost Rank': fp_rank if fp_rank < 999 else "N/A",
                    'Arbitrage Surplus': surplus_val
                })
                
            df_stacks = pd.DataFrame(stack_data).sort_values(by='Combined Stack FPS', ascending=False)
            st.dataframe(df_stacks, use_container_width=True)
            
            st.markdown("---")
            st.subheader("⚡ Double-Stack Multiplier Calculator")
            selected_catchers = st.multiselect("Select 2 Catcher Partners for Double Stack", df_catchers['PLAYER'].tolist(), default=df_catchers['PLAYER'].tolist()[:2] if len(df_catchers) >= 2 else df_catchers['PLAYER'].tolist())
            
            if len(selected_catchers) >= 2:
                df_sub = df_stacks[df_stacks['Pass Catcher'].isin(selected_catchers)]
                combined_tgt_share = df_catchers[df_catchers['PLAYER'].isin(selected_catchers)]['TGT SHARE'].sum()
                double_stack_fps = qb_fps + sum(df_sub['Catcher FPS'])
                
                col_ds1, col_ds2, col_ds3 = st.columns(3)
                col_ds1.metric("Double-Stack Total Points", round(double_stack_fps, 1))
                col_ds2.metric("Target Capture Rate", f"{round(combined_tgt_share*100, 1)}%")
                col_ds3.metric("Pass TD Capture Rate", "~85-90%")
                
                st.success(f"🔥 Holding {sel_qb} + {', '.join(selected_catchers)} captures **{round(combined_tgt_share*100, 1)}%** of {qb_team}'s entire passing volume!")

    # --- TAB 4: PRESEASON TRADE SPY ---
    with tabs[4]:
        df_undrafted_calc = df_calc[~df_calc['Player'].isin(st.session_state.drafted_all)].reset_index(drop=True)
        render_trade_analyzer(df_calc, df_undrafted_calc, run_monte_carlo_sims)