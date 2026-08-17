import streamlit as st
import pandas as pd
import numpy as np

# Built-in Baseline Data for 2026 NFL D/ST & Offensive Line Metrics
# (Can be overridden dynamically via sliders / inputs)
DEFAULT_DST_METRICS = {
    'JAX': {'Team': 'Jacksonville Jaguars', 'Pressure_Rate': 24.8, 'Sack_Rate': 7.4, 'Blitz_Rate': 28.0, 'Base_Tier': 'Streamer'},
    'CIN': {'Team': 'Cincinnati Bengals', 'Pressure_Rate': 22.1, 'Sack_Rate': 6.8, 'Blitz_Rate': 24.5, 'Base_Tier': 'Rostered'},
    'CLE': {'Team': 'Cleveland Browns', 'Pressure_Rate': 28.5, 'Sack_Rate': 8.9, 'Blitz_Rate': 31.0, 'Base_Tier': 'Elite'},
    'SF':  {'Team': 'San Francisco 49ers', 'Pressure_Rate': 26.2, 'Sack_Rate': 7.9, 'Blitz_Rate': 22.0, 'Base_Tier': 'Elite'},
    'BAL': {'Team': 'Baltimore Ravens', 'Pressure_Rate': 25.0, 'Sack_Rate': 7.6, 'Blitz_Rate': 29.5, 'Base_Tier': 'Elite'},
    'PIT': {'Team': 'Pittsburgh Steelers', 'Pressure_Rate': 27.1, 'Sack_Rate': 8.4, 'Blitz_Rate': 33.0, 'Base_Tier': 'Elite'},
    'DEN': {'Team': 'Denver Broncos', 'Pressure_Rate': 24.0, 'Sack_Rate': 7.2, 'Blitz_Rate': 27.0, 'Base_Tier': 'Streamer'},
    'SEA': {'Team': 'Seattle Seahawks', 'Pressure_Rate': 23.5, 'Sack_Rate': 6.9, 'Blitz_Rate': 26.0, 'Base_Tier': 'Streamer'},
    'NYJ': {'Team': 'New York Jets', 'Pressure_Rate': 26.8, 'Sack_Rate': 8.1, 'Blitz_Rate': 21.5, 'Base_Tier': 'Elite'},
    'HOU': {'Team': 'Houston Texans', 'Pressure_Rate': 25.4, 'Sack_Rate': 7.7, 'Blitz_Rate': 25.0, 'Base_Tier': 'Rostered'},
    'DAL': {'Team': 'Dallas Cowboys', 'Pressure_Rate': 26.0, 'Sack_Rate': 7.8, 'Blitz_Rate': 30.0, 'Base_Tier': 'Rostered'},
    'TB':  {'Team': 'Tampa Bay Buccaneers', 'Pressure_Rate': 23.0, 'Sack_Rate': 6.7, 'Blitz_Rate': 34.0, 'Base_Tier': 'Streamer'},
    'NE':  {'Team': 'New England Patriots', 'Pressure_Rate': 21.0, 'Sack_Rate': 5.9, 'Blitz_Rate': 23.0, 'Base_Tier': 'Low-Tier'},
    'CAR': {'Team': 'Carolina Panthers', 'Pressure_Rate': 18.5, 'Sack_Rate': 5.2, 'Blitz_Rate': 22.0, 'Base_Tier': 'Low-Tier'},
    'TEN': {'Team': 'Tennessee Titans', 'Pressure_Rate': 20.5, 'Sack_Rate': 5.8, 'Blitz_Rate': 25.0, 'Base_Tier': 'Low-Tier'},
    'LV':  {'Team': 'Las Vegas Raiders', 'Pressure_Rate': 22.8, 'Sack_Rate': 6.9, 'Blitz_Rate': 24.0, 'Base_Tier': 'Streamer'}
}

DEFAULT_OPPONENT_METRICS = {
    'CLE': {'OL_Pressure_Allowed': 27.5, 'QB_Sack_Avoidance_Penalty': 1.25, 'Turnover_Rate': 2.4, 'Implied_Pass_Bias': 'High'},
    'CAR': {'OL_Pressure_Allowed': 28.0, 'QB_Sack_Avoidance_Penalty': 1.30, 'Turnover_Rate': 2.6, 'Implied_Pass_Bias': 'Extreme'},
    'TEN': {'OL_Pressure_Allowed': 26.5, 'QB_Sack_Avoidance_Penalty': 1.20, 'Turnover_Rate': 2.2, 'Implied_Pass_Bias': 'Moderate'},
    'NE':  {'OL_Pressure_Allowed': 29.0, 'QB_Sack_Avoidance_Penalty': 1.35, 'Turnover_Rate': 2.5, 'Implied_Pass_Bias': 'High'},
    'NYG': {'OL_Pressure_Allowed': 30.2, 'QB_Sack_Avoidance_Penalty': 1.40, 'Turnover_Rate': 2.7, 'Implied_Pass_Bias': 'Extreme'},
    'LV':  {'OL_Pressure_Allowed': 25.0, 'QB_Sack_Avoidance_Penalty': 1.15, 'Turnover_Rate': 2.1, 'Implied_Pass_Bias': 'Moderate'},
    'DEN': {'OL_Pressure_Allowed': 24.0, 'QB_Sack_Avoidance_Penalty': 1.10, 'Turnover_Rate': 1.9, 'Implied_Pass_Bias': 'Moderate'},
    'DET': {'OL_Pressure_Allowed': 15.5, 'QB_Sack_Avoidance_Penalty': 0.75, 'Turnover_Rate': 1.1, 'Implied_Pass_Bias': 'Low'},
    'PHI': {'OL_Pressure_Allowed': 16.8, 'QB_Sack_Avoidance_Penalty': 0.80, 'Turnover_Rate': 1.2, 'Implied_Pass_Bias': 'Low'},
    'KC':  {'OL_Pressure_Allowed': 17.0, 'QB_Sack_Avoidance_Penalty': 0.70, 'Turnover_Rate': 1.0, 'Implied_Pass_Bias': 'Low'},
    'BUF': {'OL_Pressure_Allowed': 18.0, 'QB_Sack_Avoidance_Penalty': 0.75, 'Turnover_Rate': 1.3, 'Implied_Pass_Bias': 'Low'}
}

# 3-Week Schedule Lookahead Map (Week 1, Week 2, Week 3)
SAMPLE_SCHEDULE = {
    'JAX': [('CLE', -3.5, 41.5, 'Home'), ('TEN', -4.0, 42.0, 'Away'), ('CAR', -6.5, 40.0, 'Home')],
    'CIN': [('NE', -7.5, 41.0, 'Home'),  ('KC', +3.5, 48.0, 'Away'),   ('WSH', -5.5, 44.5, 'Home')],
    'DEN': [('SEA', +4.5, 42.0, 'Away'), ('PIT', -1.5, 38.5, 'Home'),  ('TB', +3.0, 43.5, 'Away')],
    'SEA': [('DEN', -4.5, 42.0, 'Home'), ('NE', -3.5, 39.5, 'Away'),   ('MIA', +4.0, 46.0, 'Home')],
    'TB':  [('WSH', -3.0, 43.0, 'Home'), ('DET', +6.5, 51.0, 'Away'),  ('DEN', -3.0, 43.5, 'Home')],
    'CLE': [('DAL', +2.5, 43.5, 'Home'), ('JAX', +3.5, 41.5, 'Away'),  ('NYG', -4.5, 39.0, 'Home')],
    'SF':  [('NYJ', -4.5, 43.0, 'Home'), ('MIN', -6.0, 45.5, 'Away'),  ('LAR', -3.5, 46.0, 'Away')],
    'BAL': [('KC', +3.0, 47.0, 'Away'),  ('LV', -8.5, 41.0, 'Home'),   ('DAL', -1.5, 46.5, 'Away')],
    'PIT': [('ATL', +3.0, 42.0, 'Away'), ('DEN', +1.5, 38.5, 'Away'),  ('LAC', -2.5, 40.5, 'Home')],
    'HOU': [('IND', -2.5, 48.5, 'Away'), ('CHI', -6.0, 45.0, 'Home'),  ('MIN', -3.5, 44.0, 'Away')]
}

def calculate_dst_composite_score(dst_code, opp_code, spread, ou_total, is_home):
    dst_data = DEFAULT_DST_METRICS.get(dst_code, {'Pressure_Rate': 22.0, 'Sack_Rate': 6.5, 'Blitz_Rate': 25.0})
    opp_data = DEFAULT_OPPONENT_METRICS.get(opp_code, {'OL_Pressure_Allowed': 23.0, 'QB_Sack_Avoidance_Penalty': 1.0, 'Turnover_Rate': 1.8})
    
    # 1. Implied Totals
    implied_opp_total = (ou_total / 2.0) - (spread / 2.0)
    implied_dst_total = (ou_total / 2.0) + (spread / 2.0)
    
    # 2. Pressure & Sack Index
    combined_pressure_idx = (dst_data['Pressure_Rate'] * 0.45) + (opp_data['OL_Pressure_Allowed'] * 0.55)
    expected_sacks = (dst_data['Sack_Rate'] * opp_data['QB_Sack_Avoidance_Penalty']) * (combined_pressure_idx / 22.0)
    expected_sack_pts = expected_sacks * 1.0 # 1 pt per sack
    
    # 3. Game Script & Turnover Equity
    # Negative spread = favorite (more likely to lead and force passes)
    trailing_pressure_multiplier = 1.25 if spread <= -4.0 else (1.10 if spread < 0 else 0.85)
    expected_turnovers = (opp_data['Turnover_Rate'] * 0.55 + (0.5 if is_home else 0.0)) * trailing_pressure_multiplier
    expected_to_pts = expected_turnovers * 2.0 # 2 pts per takeaway
    
    # 4. Points Allowed Tier Equity
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
        
    # 5. Volatility & Defensive TD Probability (~9-12% baseline for high pressure favorites)
    td_equity = (expected_turnovers * 0.08) * 6.0
    
    composite_raw = expected_sack_pts + expected_to_pts + pts_allowed_equity + td_equity
    return {
        'Composite_Score': round(composite_raw, 2),
        'Expected_Sacks': round(expected_sacks, 1),
        'Expected_Takeaways': round(expected_turnovers, 1),
        'Implied_Opp_Points': round(implied_opp_total, 1),
        'Sack_Floor_Rating': '🔥 Elite' if expected_sacks >= 3.5 else ('🟢 High' if expected_sacks >= 2.8 else '🟡 Moderate')
    }

def render_dst_streaming_terminal():
    st.header("🛡️ D/ST Asymmetric Streaming Terminal")
    st.caption("Game-Script Volatility, Pass-Protection Deficit Index & Vegas Implied Line Analytics")
    
    col_t1, col_t2, col_t3 = st.columns([1.5, 1.5, 2])
    
    selected_streamer = col_t1.selectbox(
        "Target D/ST to Evaluate", 
        list(SAMPLE_SCHEDULE.keys()), 
        index=0 # Default to Jacksonville (JAX)
    )
    
    current_matchup = SAMPLE_SCHEDULE[selected_streamer][0] # Week 1 Matchup
    opp_team = col_t2.selectbox("Week 1 Opponent", list(DEFAULT_OPPONENT_METRICS.keys()), index=list(DEFAULT_OPPONENT_METRICS.keys()).index(current_matchup[0]))
    
    col_v1, col_v2, col_v3 = st.columns(3)
    spread_input = col_v1.number_input("Vegas Point Spread (Negative = Favored)", -20.0, 20.0, float(current_matchup[1]), 0.5)
    ou_input = col_v2.number_input("Game Over/Under (O/U)", 30.0, 60.0, float(current_matchup[2]), 0.5)
    location_input = col_v3.radio("Game Location", ["Home", "Away"], index=0 if current_matchup[3] == 'Home' else 1, horizontal=True)
    
    eval_res = calculate_dst_composite_score(
        selected_streamer, 
        opp_team, 
        spread_input, 
        ou_input, 
        location_input == "Home"
    )
    
    st.markdown("---")
    st.subheader(f"📊 Week 1 Projection: **{DEFAULT_DST_METRICS[selected_streamer]['Team']} vs. {opp_team}**")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projected D/ST Points", f"{eval_res['Composite_Score']} PTS")
    m2.metric("Projected Sacks", f"{eval_res['Expected_Sacks']}")
    m3.metric("Projected Takeaways", f"{eval_res['Expected_Takeaways']}")
    m4.metric("Opp. Implied Total", f"{eval_res['Implied_Opp_Points']} PTS")
    
    if eval_res['Composite_Score'] >= 8.5:
        st.success(f"🟢 **STREAMING VERDICT: SMASH START.** {selected_streamer} combines a strong pressure rate with an advantageous Vegas game script ({spread_input} spread). High sack/turnover floor.")
    elif eval_res['Composite_Score'] >= 6.5:
        st.info(f"🔵 **STREAMING VERDICT: SOLID START.** {selected_streamer} provides a stable scoring floor with moderate turnover equity.")
    else:
        st.warning(f"⚠️ **STREAMING VERDICT: LOW CEILING / AVOID.** Low sack upside or unfavorable implied script.")
        
    st.markdown("---")
    st.subheader("📅 3-Week Stash & Stream Trajectory Matrix")
    st.caption("Identify multi-week pairs before waiver prices spike next Tuesday:")
    
    trajectory_data = []
    for d_code, weeks in SAMPLE_SCHEDULE.items():
        w1, w2, w3 = weeks[0], weeks[1], weeks[2]
        r1 = calculate_dst_composite_score(d_code, w1[0], w1[1], w1[2], w1[3]=='Home')['Composite_Score']
        r2 = calculate_dst_composite_score(d_code, w2[0], w2[1], w2[2], w2[3]=='Home')['Composite_Score']
        r3 = calculate_dst_composite_score(d_code, w3[0], w3[1], w3[2], w3[3]=='Home')['Composite_Score']
        avg_score = round((r1 + r2 + r3) / 3.0, 2)
        
        trajectory_data.append({
            'D/ST Code': d_code,
            'Team Name': DEFAULT_DST_METRICS[d_code]['Team'],
            'Week 1 Matchup': f"{w1[0]} ({w1[1]}) -> {r1} pts",
            'Week 2 Matchup': f"{w2[0]} ({w2[1]}) -> {r2} pts",
            'Week 3 Matchup': f"{w3[0]} ({w3[1]}) -> {r3} pts",
            '3-Week Composite Score': avg_score,
            'Streaming Action': '🔥 Must Hold (Multi-Week)' if avg_score >= 8.0 else ('🟢 1-Week Stream' if r1 >= 8.0 else '🟡 Stash for W2/W3' if r2 >= 8.0 else '⚪ Pass')
        })
        
    df_traj = pd.DataFrame(trajectory_data).sort_values(by='3-Week Composite Score', ascending=False)
    st.dataframe(df_traj, use_container_width=True)