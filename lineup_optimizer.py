import streamlit as st
import pandas as pd
import numpy as np

MY_CURRENT_ROSTER = [
    {"Player": "Dak Prescott", "Pos": "QB", "Team": "DAL"},
    {"Player": "Jared Goff", "Pos": "QB", "Team": "DET"},
    {"Player": "Chase Brown", "Pos": "RB", "Team": "CIN"},
    {"Player": "Omarion Hampton", "Pos": "RB", "Team": "LAC"},
    {"Player": "Bucky Irving", "Pos": "RB", "Team": "TB"},
    {"Player": "Tony Pollard", "Pos": "RB", "Team": "TEN"},
    {"Player": "RJ Harvey", "Pos": "RB", "Team": "DEN"},
    {"Player": "Jonah Coleman", "Pos": "RB", "Team": "DEN"},
    {"Player": "Drake London", "Pos": "WR", "Team": "ATL"},
    {"Player": "DJ Moore", "Pos": "WR", "Team": "BUF"},
    {"Player": "Wan'Dale Robinson", "Pos": "WR", "Team": "TEN"},
    {"Player": "Josh Downs", "Pos": "WR", "Team": "IND"},
    {"Player": "Jayden Higgins", "Pos": "WR", "Team": "HOU"},
    {"Player": "Jalen McMillan", "Pos": "WR", "Team": "TB"},
    {"Player": "Jacksonville D/ST", "Pos": "DST", "Team": "JAX"}
]

def clean_name(val):
    if not isinstance(val, str):
        return ""
    name_clean = val.strip()
    for suffix in [' III', ' II', ' Jr.', ' Sr.', ' Jr', ' Sr']:
        if name_clean.endswith(suffix):
            name_clean = name_clean[:-len(suffix)]
    return name_clean.strip().lower()

def solve_optimal_lineup(df_proj, mode="Floor (Expected)"):
    # Standardize names
    df_proj['Clean_Name'] = df_proj['Player'].apply(clean_name)
    df_roster = pd.DataFrame(MY_CURRENT_ROSTER)
    df_roster['Clean_Name'] = df_roster['Player'].apply(clean_name)
    
    # Merge projections with your current squad
    merged = pd.merge(df_roster, df_proj[['Clean_Name', 'Proj_PTS', 'Floor_PTS', 'Ceiling_PTS']], on='Clean_Name', how='left')
    merged['Proj_PTS'] = merged['Proj_PTS'].fillna(8.0)
    merged['Floor_PTS'] = merged['Floor_PTS'].fillna(merged['Proj_PTS'] * 0.70)
    merged['Ceiling_PTS'] = merged['Ceiling_PTS'].fillna(merged['Proj_PTS'] * 1.35)
    
    # Select sorting metric
    if mode == "Ceiling Chaser (Underdog)":
        merged['Metric'] = merged['Ceiling_PTS']
    elif mode == "Floor Maximizer (Favored)":
        merged['Metric'] = merged['Floor_PTS']
    else:
        merged['Metric'] = merged['Proj_PTS']
        
    merged = merged.sort_values(by='Metric', ascending=False).reset_index(drop=True)
    
    # Roster Slots: 1 QB, 2 RB, 2 WR, 1 WR/TE Flex, 1 FLEX (W/R/T), 1 OP (Superflex), 1 D/ST
    lineup = {}
    used_players = set()
    
    # 1. QB1 Slot
    qbs = merged[(merged['Pos'] == 'QB') & (~merged['Clean_Name'].isin(used_players))]
    if not qbs.empty:
        p = qbs.iloc[0]
        lineup['QB1'] = p
        used_players.add(p['Clean_Name'])
        
    # 2. RB1 & RB2 Slots
    rbs = merged[(merged['Pos'] == 'RB') & (~merged['Clean_Name'].isin(used_players))]
    if len(rbs) >= 1:
        p1 = rbs.iloc[0]
        lineup['RB1'] = p1
        used_players.add(p1['Clean_Name'])
    if len(rbs) >= 2:
        p2 = rbs.iloc[1]
        lineup['RB2'] = p2
        used_players.add(p2['Clean_Name'])
        
    # 3. WR1 & WR2 Slots
    wrs = merged[(merged['Pos'] == 'WR') & (~merged['Clean_Name'].isin(used_players))]
    if len(wrs) >= 1:
        p1 = wrs.iloc[0]
        lineup['WR1'] = p1
        used_players.add(p1['Clean_Name'])
    if len(wrs) >= 2:
        p2 = wrs.iloc[1]
        lineup['WR2'] = p2
        used_players.add(p2['Clean_Name'])
        
    # 4. WR/TE Flex Slot
    wr_te = merged[(merged['Pos'].isin(['WR', 'TE'])) & (~merged['Clean_Name'].isin(used_players))]
    if not wr_te.empty:
        p = wr_te.iloc[0]
        lineup['WR/TE Flex'] = p
        used_players.add(p['Clean_Name'])
        
    # 5. Regular Flex Slot (RB/WR/TE)
    flex_pool = merged[(merged['Pos'].isin(['RB', 'WR', 'TE'])) & (~merged['Clean_Name'].isin(used_players))]
    if not flex_pool.empty:
        p = flex_pool.iloc[0]
        lineup['FLEX'] = p
        used_players.add(p['Clean_Name'])
        
    # 6. OP (Superflex Slot - Can be QB, RB, WR, TE)
    op_pool = merged[~merged['Clean_Name'].isin(used_players) & (merged['Pos'] != 'DST')]
    if not op_pool.empty:
        p = op_pool.iloc[0]
        lineup['OP (Superflex)'] = p
        used_players.add(p['Clean_Name'])
        
    # 7. D/ST Slot
    dst_pool = merged[merged['Pos'] == 'DST']
    if not dst_pool.empty:
        lineup['D/ST'] = dst_pool.iloc[0]
        
    # Bench
    bench = merged[~merged['Clean_Name'].isin(used_players) & (merged['Pos'] != 'DST')]
    return lineup, bench

def render_lineup_optimizer():
    st.header("📊 Weekly Spreadsheet Ingestion & Lineup Solver")
    st.caption("Auto-solves your optimal 8-starter lineup based on weekly spreadsheet projections.")
    
    col_u1, col_u2 = st.columns([2, 1])
    uploaded_file = col_u1.file_uploader("Upload Weekly Projections (.xlsx or .csv)", type=['xlsx', 'csv'])
    opt_mode = col_u2.selectbox("Optimization Strategy", ["Expected Points (Median)", "Floor Maximizer (Favored)", "Ceiling Chaser (Underdog)"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
                
            # Standardize column headers
            cols_map = {c.upper(): c for c in df_raw.columns}
            p_col = cols_map.get('PLAYER', cols_map.get('NAME', df_raw.columns[0]))
            pts_col = cols_map.get('PROJ_PTS', cols_map.get('PTS', cols_map.get('FPS', df_raw.columns[1])))
            
            df_std = pd.DataFrame({
                'Player': df_raw[p_col],
                'Proj_PTS': pd.to_numeric(df_raw[pts_col], errors='coerce')
            }).dropna()
            
            lineup_dict, bench_df = solve_optimal_lineup(df_std, mode=opt_mode)
            
            st.markdown("---")
            st.subheader(f"🏆 Optimal Week 1 Starting Lineup: **{opt_mode}**")
            
            table_rows = []
            total_proj = 0.0
            for slot, p_data in lineup_dict.items():
                pts = round(p_data['Metric'], 1)
                total_proj += pts
                table_rows.append({
                    'Roster Slot': slot,
                    'Starting Player': p_data['Player'],
                    'Pos': p_data['Pos'],
                    'NFL Team': p_data['Team'],
                    'Projected Output': f"{pts} PTS"
                })
                
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
            st.metric("Total Optimal Lineup Projection", f"{round(total_proj, 1)} PTS")
            
            st.markdown("---")
            st.subheader("🛋️ Bench Contingency Depth")
            st.dataframe(bench_df[['Player', 'Pos', 'Team', 'Proj_PTS', 'Floor_PTS', 'Ceiling_PTS']], use_container_width=True)
            
        except Exception as e:
            st.error(f"Error parsing weekly file: {e}")
    else:
        st.info("💡 **Ready for Ingestion:** Drag and drop your weekly projections file above on Tuesday/Wednesday to solve your starting lineup.")