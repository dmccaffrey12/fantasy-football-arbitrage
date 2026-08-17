import streamlit as st
import pandas as pd
import numpy as np

# COMPLETE 32 NFL TEAM NAMES & CODES
NFL_TEAMS = {
    'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens', 'BUF': 'Buffalo Bills',
    'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears', 'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns',
    'DAL': 'Dallas Cowboys', 'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
    'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars', 'KC': 'Kansas City Chiefs',
    'LAC': 'Los Angeles Chargers', 'LAR': 'Los Angeles Rams', 'LV': 'Las Vegas Raiders', 'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings', 'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants',
    'NYJ': 'New York Jets', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers', 'SEA': 'Seattle Seahawks',
    'SF': 'San Francisco 49ers', 'TB': 'Tampa Bay Buccaneers', 'TEN': 'Tennessee Titans', 'WSH': 'Washington Commanders'
}

# 32-TEAM DEFENSE PRESSURE & TURNOVER METRICS
DEFAULT_DST_METRICS = {
    'CLE': {'Pressure_Rate': 28.5, 'Sack_Rate': 8.9, 'Blitz_Rate': 31.0, 'Base_Tier': 'Elite'},
    'PIT': {'Pressure_Rate': 27.1, 'Sack_Rate': 8.4, 'Blitz_Rate': 33.0, 'Base_Tier': 'Elite'},
    'NYJ': {'Pressure_Rate': 26.8, 'Sack_Rate': 8.1, 'Blitz_Rate': 21.5, 'Base_Tier': 'Elite'},
    'SF':  {'Pressure_Rate': 26.2, 'Sack_Rate': 7.9, 'Blitz_Rate': 22.0, 'Base_Tier': 'Elite'},
    'DAL': {'Pressure_Rate': 26.0, 'Sack_Rate': 7.8, 'Blitz_Rate': 30.0, 'Base_Tier': 'Elite'},
    'HOU': {'Pressure_Rate': 25.4, 'Sack_Rate': 7.7, 'Blitz_Rate': 25.0, 'Base_Tier': 'Rostered'},
    'BAL': {'Pressure_Rate': 25.0, 'Sack_Rate': 7.6, 'Blitz_Rate': 29.5, 'Base_Tier': 'Elite'},
    'JAX': {'Pressure_Rate': 24.8, 'Sack_Rate': 7.4, 'Blitz_Rate': 28.0, 'Base_Tier': 'Streamer'},
    'DEN': {'Pressure_Rate': 24.0, 'Sack_Rate': 7.2, 'Blitz_Rate': 27.0, 'Base_Tier': 'Streamer'},
    'SEA': {'Pressure_Rate': 23.5, 'Sack_Rate': 6.9, 'Blitz_Rate': 26.0, 'Base_Tier': 'Streamer'},
    'TB':  {'Pressure_Rate': 23.0, 'Sack_Rate': 6.7, 'Blitz_Rate': 34.0, 'Base_Tier': 'Streamer'},
    'LV':  {'Pressure_Rate': 22.8, 'Sack_Rate': 6.9, 'Blitz_Rate': 24.0, 'Base_Tier': 'Streamer'},
    'CIN': {'Pressure_Rate': 22.1, 'Sack_Rate': 6.8, 'Blitz_Rate': 24.5, 'Base_Tier': 'Rostered'},
    'KC':  {'Pressure_Rate': 22.5, 'Sack_Rate': 6.6, 'Blitz_Rate': 27.0, 'Base_Tier': 'Rostered'},
    'GB':  {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 26.0, 'Base_Tier': 'Streamer'},
    'IND': {'Pressure_Rate': 21.8, 'Sack_Rate': 6.4, 'Blitz_Rate': 21.0, 'Base_Tier': 'Streamer'},
    'BUF': {'Pressure_Rate': 22.4, 'Sack_Rate': 6.6, 'Blitz_Rate': 23.0, 'Base_Tier': 'Rostered'},
    'PHI': {'Pressure_Rate': 22.0, 'Sack_Rate': 6.4, 'Blitz_Rate': 22.5, 'Base_Tier': 'Rostered'},
    'MIN': {'Pressure_Rate': 23.2, 'Sack_Rate': 6.8, 'Blitz_Rate': 38.0, 'Base_Tier': 'Streamer'},
    'DET': {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 25.0, 'Base_Tier': 'Rostered'},
    'LAR': {'Pressure_Rate': 21.5, 'Sack_Rate': 6.3, 'Blitz_Rate': 24.0, 'Base_Tier': 'Streamer'},
    'MIA': {'Pressure_Rate': 21.4, 'Sack_Rate': 6.2, 'Blitz_Rate': 27.0, 'Base_Tier': 'Streamer'},
    'LAC': {'Pressure_Rate': 21.2, 'Sack_Rate': 6.1, 'Blitz_Rate': 23.0, 'Base_Tier': 'Streamer'},
    'NO':  {'Pressure_Rate': 21.0, 'Sack_Rate': 6.0, 'Blitz_Rate': 24.0, 'Base_Tier': 'Streamer'},
    'NE':  {'Pressure_Rate': 21.0, 'Sack_Rate': 5.9, 'Blitz_Rate': 23.0, 'Base_Tier': 'Low-Tier'},
    'CHI': {'Pressure_Rate': 20.8, 'Sack_Rate': 5.8, 'Blitz_Rate': 22.0, 'Base_Tier': 'Streamer'},
    'TEN': {'Pressure_Rate': 20.5, 'Sack_Rate': 5.8, 'Blitz_Rate': 25.0, 'Base_Tier': 'Low-Tier'},
    'ATL': {'Pressure_Rate': 20.0, 'Sack_Rate': 5.5, 'Blitz_Rate': 22.0, 'Base_Tier': 'Low-Tier'},
    'WSH': {'Pressure_Rate': 19.5, 'Sack_Rate': 5.4, 'Blitz_Rate': 24.0, 'Base_Tier': 'Low-Tier'},
    'ARI': {'Pressure_Rate': 19.0, 'Sack_Rate': 5.3, 'Blitz_Rate': 21.0, 'Base_Tier': 'Low-Tier'},
    'CAR': {'Pressure_Rate': 18.5, 'Sack_Rate': 5.2, 'Blitz_Rate': 22.0, 'Base_Tier': 'Low-Tier'},
    'NYG': {'Pressure_Rate': 20.5, 'Sack_Rate': 5.7, 'Blitz_Rate': 28.0, 'Base_Tier': 'Low-Tier'}
}

# 32-TEAM OFFENSIVE LINE & TURNOVER VULNERABILITY METRICS
DEFAULT_OPPONENT_METRICS = {
    'NYG': {'OL_Pressure_Allowed': 30.2, 'QB_Sack_Penalty': 1.40, 'Turnover_Rate': 2.7},
    'NE':  {'OL_Pressure_Allowed': 29.0, 'QB_Sack_Penalty': 1.35, 'Turnover_Rate': 2.5},
    'CAR': {'OL_Pressure_Allowed': 28.0, 'QB_Sack_Penalty': 1.30, 'Turnover_Rate': 2.6},
    'CLE': {'OL_Pressure_Allowed': 27.5, 'QB_Sack_Penalty': 1.25, 'Turnover_Rate': 2.4},
    'TEN': {'OL_Pressure_Allowed': 26.5, 'QB_Sack_Penalty': 1.20, 'Turnover_Rate': 2.2},
    'WSH': {'OL_Pressure_Allowed': 25.8, 'QB_Sack_Penalty': 1.20, 'Turnover_Rate': 2.3},
    'LV':  {'OL_Pressure_Allowed': 25.0, 'QB_Sack_Penalty': 1.15, 'Turnover_Rate': 2.1},
    'ARI': {'OL_Pressure_Allowed': 24.5, 'QB_Sack_Penalty': 1.15, 'Turnover_Rate': 2.0},
    'DEN': {'OL_Pressure_Allowed': 24.0, 'QB_Sack_Penalty': 1.10, 'Turnover_Rate': 1.9},
    'SEA': {'OL_Pressure_Allowed': 24.2, 'QB_Sack_Penalty': 1.10, 'Turnover_Rate': 1.9},
    'NO':  {'OL_Pressure_Allowed': 23.5, 'QB_Sack_Penalty': 1.05, 'Turnover_Rate': 1.8},
    'TB':  {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Penalty': 1.00, 'Turnover_Rate': 1.8},
    'CHI': {'OL_Pressure_Allowed': 24.8, 'QB_Sack_Penalty': 1.15, 'Turnover_Rate': 2.1},
    'MIN': {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Penalty': 1.05, 'Turnover_Rate': 1.8},
    'ATL': {'OL_Pressure_Allowed': 22.0, 'QB_Sack_Penalty': 1.00, 'Turnover_Rate': 1.7},
    'LAC': {'OL_Pressure_Allowed': 21.5, 'QB_Sack_Penalty': 0.95, 'Turnover_Rate': 1.6},
    'PIT': {'OL_Pressure_Allowed': 22.8, 'QB_Sack_Penalty': 1.05, 'Turnover_Rate': 1.8},
    'JAX': {'OL_Pressure_Allowed': 21.0, 'QB_Sack_Penalty': 0.95, 'Turnover_Rate': 1.6},
    'MIA': {'OL_Pressure_Allowed': 20.5, 'QB_Sack_Penalty': 0.90, 'Turnover_Rate': 1.5},
    'IND': {'OL_Pressure_Allowed': 19.5, 'QB_Sack_Penalty': 0.85, 'Turnover_Rate': 1.4},
    'LAR': {'OL_Pressure_Allowed': 20.0, 'QB_Sack_Penalty': 0.90, 'Turnover_Rate': 1.5},
    'CIN': {'OL_Pressure_Allowed': 21.0, 'QB_Sack_Penalty': 0.95, 'Turnover_Rate': 1.5},
    'GB':  {'OL_Pressure_Allowed': 18.5, 'QB_Sack_Penalty': 0.80, 'Turnover_Rate': 1.3},
    'HOU': {'OL_Pressure_Allowed': 19.0, 'QB_Sack_Penalty': 0.85, 'Turnover_Rate': 1.4},
    'DAL': {'OL_Pressure_Allowed': 18.0, 'QB_Sack_Penalty': 0.80, 'Turnover_Rate': 1.3},
    'SF':  {'OL_Pressure_Allowed': 18.2, 'QB_Sack_Penalty': 0.80, 'Turnover_Rate': 1.3},
    'BAL': {'OL_Pressure_Allowed': 17.5, 'QB_Sack_Penalty': 0.75, 'Turnover_Rate': 1.2},
    'BUF': {'OL_Pressure_Allowed': 18.0, 'QB_Sack_Penalty': 0.75, 'Turnover_Rate': 1.3},
    'KC':  {'OL_Pressure_Allowed': 17.0, 'QB_Sack_Penalty': 0.70, 'Turnover_Rate': 1.0},
    'PHI': {'OL_Pressure_Allowed': 16.8, 'QB_Sack_Penalty': 0.80, 'Turnover_Rate': 1.2},
    'DET': {'OL_Pressure_Allowed': 15.5, 'QB_Sack_Penalty': 0.75, 'Turnover_Rate': 1.1},
    'NYJ': {'OL_Pressure_Allowed': 19.5, 'QB_Sack_Penalty': 0.85, 'Turnover_Rate': 1.4}
}

# 3-WEEK NFL SCHEDULE & VEGAS ODDS LOOKAHEAD MAP
FULL_NFL_SCHEDULE = {
    'JAX': [('CLE', -3.5, 41.5, 'Home'), ('TEN', -4.0, 42.0, 'Away'), ('CAR', -6.5, 40.0, 'Home')],
    'CIN': [('NE', -7.5, 41.0, 'Home'),  ('KC', +3.5, 48.0, 'Away'),   ('WSH', -5.5, 44.5, 'Home')],
    'DEN': [('SEA', +4.5, 42.0, 'Away'), ('PIT', -1.5, 38.5, 'Home'),  ('TB', +3.0, 43.5, 'Away')],
    'SEA': [('DEN', -4.5, 42.0, 'Home'), ('NE', -3.5, 39.5, 'Away'),   ('MIA', +4.0, 46.0, 'Home')],
    'TB':  [('WSH', -3.0, 43.0, 'Home'), ('DET', +6.5, 51.0, 'Away'),  ('DEN', -3.0, 43.5, 'Home')],
    'CLE': [('DAL', +2.5, 43.5, 'Home'), ('JAX', +3.5, 41.5, 'Away'),  ('NYG', -4.5, 39.0, 'Home')],
    'SF':  [('NYJ', -4.5, 43.0, 'Home'), ('MIN', -6.0, 45.5, 'Away'),  ('LAR', -3.5, 46.0, 'Away')],
    'BAL': [('KC', +3.0, 47.0, 'Away'),  ('LV', -8.5, 41.0, 'Home'),   ('DAL', -1.5, 46.5, 'Away')],
    'PIT': [('ATL', +3.0, 42.0, 'Away'), ('DEN', +1.5, 38.5, 'Away'),  ('LAC', -2.5, 40.5, 'Home')],
    'HOU': [('IND', -2.5, 48.5, 'Away'), ('CHI', -6.0, 45.0, 'Home'),  ('MIN', -3.5, 44.0, 'Away')],
    'DAL': [('CLE', -2.5, 43.5, 'Away'), ('NO', -6.5, 45.5, 'Home'),   ('BAL', +1.5, 46.5, 'Home')],
    'NYJ': [('SF', +4.5, 43.0, 'Away'),  ('TEN', -3.5, 41.0, 'Away'),  ('NE', -6.5, 39.5, 'Home')],
    'KC':  [('BAL', -3.0, 47.0, 'Home'), ('CIN', -3.5, 48.0, 'Home'),  ('ATL', -4.5, 46.5, 'Away')],
    'PHI': [('GB', -2.5, 48.5, 'Neutral'), ('ATL', -6.5, 47.0, 'Home'), ('NO', -3.0, 45.0, 'Away')],
    'MIA': [('JAX', -3.5, 49.0, 'Home'), ('BUF', +1.5, 50.0, 'Home'),  ('SEA', -4.0, 46.0, 'Away')],
    'BUF': [('ARI', -6.5, 47.5, 'Home'), ('MIA', -1.5, 50.0, 'Away'),  ('JAX', -5.0, 48.5, 'Home')],
    'IND': [('HOU', +2.5, 48.5, 'Home'), ('GB', +3.0, 46.5, 'Away'),   ('CHI', -1.5, 44.0, 'Home')],
    'GB':  [('PHI', +2.5, 48.5, 'Neutral'), ('IND', -3.0, 46.5, 'Home'), ('TEN', -3.5, 42.0, 'Away')],
    'MIN': [('NYG', -1.5, 41.5, 'Away'), ('SF', +6.0, 45.5, 'Home'),   ('HOU', +3.5, 44.0, 'Home')],
    'DET': [('LAR', -3.5, 51.0, 'Home'), ('TB', -6.5, 51.0, 'Home'),   ('ARI', -4.5, 52.0, 'Away')],
    'CHI': [('TEN', -4.0, 44.5, 'Home'), ('HOU', +6.0, 45.0, 'Away'),  ('IND', +1.5, 44.0, 'Away')],
    'LV':  [('LAC', +3.0, 42.5, 'Away'), ('BAL', +8.5, 41.0, 'Away'),  ('CAR', -5.5, 40.5, 'Home')],
    'LAC': [('LV', -3.0, 42.5, 'Home'),  ('CAR', -4.5, 40.5, 'Away'),  ('PIT', +2.5, 40.5, 'Away')],
    'LAR': [('DET', +3.5, 51.0, 'Away'), ('ARI', -1.5, 48.0, 'Away'),  ('SF', +3.5, 46.0, 'Home')],
    'NO':  [('CAR', -4.0, 41.5, 'Home'), ('DAL', +6.5, 45.5, 'Away'),  ('PHI', +3.0, 45.0, 'Home')],
    'ATL': [('PIT', -3.0, 42.0, 'Home'), ('PHI', +6.5, 47.0, 'Away'),  ('KC', +4.5, 46.5, 'Home')],
    'CAR': [('NO', +4.0, 41.5, 'Away'),  ('LAC', +4.5, 40.5, 'Home'),  ('LV', +5.5, 40.5, 'Away')],
    'TEN': [('CHI', +4.0, 44.5, 'Away'), ('NYJ', +3.5, 41.0, 'Home'),  ('GB', +3.5, 42.0, 'Home')],
    'WSH': [('TB', +3.0, 43.0, 'Away'),  ('NYG', -2.5, 42.5, 'Home'),  ('CIN', +5.5, 44.5, 'Away')],
    'ARI': [('BUF', +6.5, 47.5, 'Away'), ('LAR', +1.5, 48.0, 'Home'),  ('DET', +4.5, 52.0, 'Home')],
    'NE':  [('CIN', +7.5, 41.0, 'Away'), ('SEA', +3.5, 39.5, 'Home'),  ('NYJ', +6.5, 39.5, 'Away')],
    'NYG': [('MIN', +1.5, 41.5, 'Home'), ('WSH', +2.5, 42.5, 'Away'),  ('CLE', +4.5, 39.0, 'Away')]
}

def calculate_dst_composite_score(dst_code, opp_code, spread, ou_total, is_home):
    dst_data = DEFAULT_DST_METRICS.get(dst_code, {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 25.0})
    opp_data = DEFAULT_OPPONENT_METRICS.get(opp_code, {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Penalty': 1.0, 'Turnover_Rate': 1.8})
    
    # 1. Implied Totals
    implied_opp_total = (ou_total / 2.0) - (spread / 2.0)
    implied_dst_total = (ou_total / 2.0) + (spread / 2.0)
    
    # 2. Pressure & Sack Index
    combined_pressure_idx = (dst_data['Pressure_Rate'] * 0.45) + (opp_data['OL_Pressure_Allowed'] * 0.55)
    expected_sacks = (dst_data['Sack_Rate'] * opp_data['QB_Sack_Penalty']) * (combined_pressure_idx / 22.0)
    expected_sack_pts = expected_sacks * 1.0
    
    # 3. Game Script & Turnover Equity
    trailing_pressure_multiplier = 1.25 if spread <= -4.0 else (1.10 if spread < 0 else 0.85)
    expected_turnovers = (opp_data['Turnover_Rate'] * 0.55 + (0.4 if is_home else 0.0)) * trailing_pressure_multiplier
    expected_to_pts = expected_turnovers * 2.0
    
    # 4. Points Allowed Equity
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
        
    td_equity = (expected_turnovers * 0.08) * 6.0
    composite_raw = expected_sack_pts + expected_to_pts + pts_allowed_equity + td_equity
    
    return {
        'Composite_Score': round(composite_raw, 2),
        'Expected_Sacks': round(expected_sacks, 1),
        'Expected_Takeaways': round(expected_turnovers, 1),
        'Implied_Opp_Points': round(implied_opp_total, 1),
        'Pressure_Index': round(combined_pressure_idx, 1)
    }

def render_dst_streaming_terminal():
    st.header("🛡️ D/ST Asymmetric Streaming Terminal")
    st.caption("Pass-Rush vs. OL Deficit Index, Vegas Game-Script Equity & Multi-Week Stash Planner")
    
    # MASTER LEAGUE-WIDE RANKINGS
    st.subheader("🔥 Week 1 League-Wide D/ST Streamer Rankings")
    
    col_f1, col_f2 = st.columns([2, 1])
    waiver_only = col_f1.checkbox("Filter: Show Available Waiver Options Only", value=True)
    
    # Pre-set default rostered defenses based on common draft patterns
    rostered_defaults = ['CIN', 'BAL', 'SF', 'CLE', 'PIT', 'DAL', 'NYJ', 'HOU', 'BUF', 'KC', 'DET', 'PHI']
    
    all_teams_list = sorted(list(FULL_NFL_SCHEDULE.keys()))
    default_waivers = [t for t in all_teams_list if t not in rostered_defaults]
    
    if waiver_only:
        active_eval_teams = default_waivers
        st.caption(f"Showing **{len(active_eval_teams)}** unrostered waiver defenses (e.g. JAX, DEN, TB, SEA, MIN, CHI...).")
    else:
        active_eval_teams = all_teams_list
        st.caption(f"Showing all **32 NFL Defenses** across the league.")
        
    rankings_data = []
    for t_code in active_eval_teams:
        matchup = FULL_NFL_SCHEDULE[t_code][0] # Week 1
        opp, spread, ou, loc = matchup[0], matchup[1], matchup[2], matchup[3]
        res = calculate_dst_composite_score(t_code, opp, spread, ou, loc == 'Home')
        
        rankings_data.append({
            'Rank': 0,
            'D/ST Code': t_code,
            'Team Name': NFL_TEAMS.get(t_code, t_code),
            'Week 1 Matchup': f"{'vs' if loc=='Home' else '@'} {opp} ({spread:+.1f})",
            'Projected PTS': res['Composite_Score'],
            'Exp. Sacks': res['Expected_Sacks'],
            'Exp. Turnovers': res['Expected_Takeaways'],
            'Opp. Implied Pts': res['Implied_Opp_Points'],
            'Streaming Tier': '🔥 Top Stream (Smash)' if res['Composite_Score'] >= 8.5 else ('🟢 Solid Option' if res['Composite_Score'] >= 7.0 else '🟡 Risky' if res['Composite_Score'] >= 5.5 else '🔴 Avoid')
        })
        
    df_board = pd.DataFrame(rankings_data).sort_values(by='Projected PTS', ascending=False).reset_index(drop=True)
    df_board['Rank'] = df_board.index + 1
    
    st.dataframe(
        df_board[['Rank', 'Team Name', 'Week 1 Matchup', 'Projected PTS', 'Exp. Sacks', 'Exp. Turnovers', 'Opp. Implied Pts', 'Streaming Tier']],
        use_container_width=True
    )
    
    st.markdown("---")
    st.subheader("🔍 Single D/ST Deep Dive & Custom Vegas Simulator")
    
    col_s1, col_s2 = st.columns(2)
    selected_eval = col_s1.selectbox("Select Team to Inspect", all_teams_list, index=all_teams_list.index('JAX'))
    
    sim_matchup = FULL_NFL_SCHEDULE[selected_eval][0]
    default_opp = sim_matchup[0]
    
    # Safe index lookup
    opp_keys = sorted(list(DEFAULT_OPPONENT_METRICS.keys()))
    safe_opp_idx = opp_keys.index(default_opp) if default_opp in opp_keys else 0
    opp_team_sel = col_s2.selectbox("Opponent", opp_keys, index=safe_opp_idx)
    
    c_v1, c_v2, c_v3 = st.columns(3)
    custom_spread = c_v1.number_input("Point Spread (Negative = Favored)", -20.0, 20.0, float(sim_matchup[1]), 0.5)
    custom_ou = c_v2.number_input("Game Over/Under (O/U)", 30.0, 60.0, float(sim_matchup[2]), 0.5)
    custom_loc = c_v3.radio("Game Location", ["Home", "Away"], index=0 if sim_matchup[3]=='Home' else 1, horizontal=True)
    
    single_res = calculate_dst_composite_score(selected_eval, opp_team_sel, custom_spread, custom_ou, custom_loc == "Home")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Composite D/ST Projection", f"{single_res['Composite_Score']} PTS")
    m2.metric("Projected Sacks", f"{single_res['Expected_Sacks']}")
    m3.metric("Projected Takeaways", f"{single_res['Expected_Takeaways']}")
    m4.metric("Opponent Implied Total", f"{single_res['Implied_Opp_Points']} PTS")
    
    st.markdown("---")
    st.subheader("📅 3-Week Stash & Stream Multi-Week Matrix")
    
    multi_data = []
    for d_code in active_eval_teams:
        weeks = FULL_NFL_SCHEDULE[d_code]
        w1, w2, w3 = weeks[0], weeks[1], weeks[2]
        r1 = calculate_dst_composite_score(d_code, w1[0], w1[1], w1[2], w1[3]=='Home')['Composite_Score']
        r2 = calculate_dst_composite_score(d_code, w2[0], w2[1], w2[2], w2[3]=='Home')['Composite_Score']
        r3 = calculate_dst_composite_score(d_code, w3[0], w3[1], w3[2], w3[3]=='Home')['Composite_Score']
        avg_3w = round((r1 + r2 + r3) / 3.0, 2)
        
        multi_data.append({
            'Team': NFL_TEAMS.get(d_code, d_code),
            'Week 1': f"{'vs' if w1[3]=='Home' else '@'} {w1[0]} ({r1} pts)",
            'Week 2': f"{'vs' if w2[3]=='Home' else '@'} {w2[0]} ({r2} pts)",
            'Week 3': f"{'vs' if w3[3]=='Home' else '@'} {w3[0]} ({r3} pts)",
            '3-Week Avg': avg_3w,
            'Trajectory Play': '🔥 Multi-Week Anchor' if avg_3w >= 7.8 else ('🟢 1-Week Stream' if r1 >= 7.8 else '🟡 Stash for W2/W3' if r2 >= 7.8 else '⚪ Pass')
        })
        
    df_multi = pd.DataFrame(multi_data).sort_values(by='3-Week Avg', ascending=False).reset_index(drop=True)
    st.dataframe(df_multi, use_container_width=True)