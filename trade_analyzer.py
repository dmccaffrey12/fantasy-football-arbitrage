import streamlit as st
import pandas as pd
import numpy as np

def get_pick_vorp_estimate(pick_num, df_calc):
    """Estimates the True VORP yield of a specific draft pick slot based on the projection board."""
    if df_calc is None or df_calc.empty:
        return 0.0
    
    # Map pick number directly to index in the sorted True VORP table
    idx = max(0, min(int(pick_num) - 1, len(df_calc) - 1))
    return float(df_calc.iloc[idx]['True_VORP'])

def render_trade_analyzer(df_calc, df_undrafted, run_monte_carlo_sims_func):
    st.header("🤝 Preseason Trade & Draft Pick Arbitrage Analyzer")
    st.caption("Evaluate multi-player and draft pick trade offers based on Custom VORP, Pick Value Curves & Market Perception.")
    
    if df_calc is None or df_calc.empty:
        st.error("No projection data available to analyze trades.")
        return

    all_players = df_calc['Player'].tolist()
    
    # Build list of 180 draft picks for 12-team, 15-round draft
    all_picks = [f"Round {((i-1)//12)+1}, Pick {((i-1)%12)+1} (Overall #{i})" for i in range(1, 181)]
    
    col_give, col_get = st.columns(2)
    
    # --- LEFT SIDE: GIVING AWAY ---
    with col_give:
        st.subheader("📤 You Give (Outgoing)")
        give_players = st.multiselect(
            "Select Player(s) You Send",
            all_players,
            key="trade_give_selector"
        )
        give_picks = st.multiselect(
            "Select Draft Pick(s) You Send",
            all_picks,
            key="trade_give_picks_selector"
        )
        
    # --- RIGHT SIDE: RECEIVING ---
    with col_get:
        st.subheader("📥 You Receive (Incoming)")
        get_players = st.multiselect(
            "Select Player(s) You Receive",
            all_players,
            key="trade_get_selector"
        )
        get_picks = st.multiselect(
            "Select Draft Pick(s) You Receive",
            all_picks,
            key="trade_get_picks_selector"
        )
        
    st.markdown("---")
    
    if give_players or get_players or give_picks or get_picks:
        df_give = df_calc[df_calc['Player'].isin(give_players)].copy()
        df_get = df_calc[df_calc['Player'].isin(get_players)].copy()
        
        # Calculate Player Values
        give_player_fps = df_give['FPS'].sum() if not df_give.empty else 0.0
        give_player_vorp = df_give['True_VORP'].sum() if not df_give.empty else 0.0
        
        get_player_fps = df_get['FPS'].sum() if not df_get.empty else 0.0
        get_player_vorp = df_get['True_VORP'].sum() if not df_get.empty else 0.0
        
        # Calculate Draft Pick VORP Values
        give_pick_vorp = 0.0
        for p_str in give_picks:
            overall_num = int(p_str.split("Overall #")[1].replace(")", ""))
            give_pick_vorp += get_pick_vorp_estimate(overall_num, df_calc)
            
        get_pick_vorp = 0.0
        for p_str in get_picks:
            overall_num = int(p_str.split("Overall #")[1].replace(")", ""))
            get_pick_vorp += get_pick_vorp_estimate(overall_num, df_calc)
            
        # Total Outgoing vs Incoming VORP
        total_give_vorp = give_player_vorp + give_pick_vorp
        total_get_vorp = get_player_vorp + get_pick_vorp
        
        # Roster Slot Balancing
        total_give_assets = len(give_players) + len(give_picks)
        total_get_assets = len(get_players) + len(get_picks)
        slot_diff = len(give_players) - len(get_players)
        
        slot_adjustment = 0.0
        if slot_diff > 0:
            replacement_val = df_undrafted.iloc[min(10, len(df_undrafted)-1)]['True_VORP'] if not df_undrafted.empty else 0.0
            slot_adjustment = slot_diff * replacement_val
            st.info(f"💡 **Roster Slot Advantage:** Receiving fewer players opens **{slot_diff}** bench slot(s). Adding **+{round(slot_adjustment, 1)} VORP** for replacement-level pickup potential.")
        elif slot_diff < 0:
            replacement_val = df_undrafted.iloc[min(10, len(df_undrafted)-1)]['True_VORP'] if not df_undrafted.empty else 0.0
            slot_adjustment = slot_diff * replacement_val
            st.warning(f"⚠️ **Roster Slot Penalty:** Receiving more players forces **{abs(slot_diff)}** roster drop(s). Deducting **{round(slot_adjustment, 1)} VORP** for lost roster flexibility.")
            
        adjusted_get_vorp = total_get_vorp + slot_adjustment
        net_vorp_shift = adjusted_get_vorp - total_give_vorp
        
        # Display Core Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Outgoing Total VORP", round(total_give_vorp, 1))
        m2.metric("Incoming Total VORP", round(total_get_vorp, 1))
        m3.metric("Draft Pick Value Delta", f"{'+' if (get_pick_vorp - give_pick_vorp) >= 0 else ''}{round(get_pick_vorp - give_pick_vorp, 1)} VORP")
        m4.metric(
            "Net Trade VORP Δ", 
            f"{'+' if net_vorp_shift >= 0 else ''}{round(net_vorp_shift, 1)}",
            delta=f"{round(net_vorp_shift, 1)} VORP",
            delta_color="normal" if net_vorp_shift >= 0 else "inverse"
        )
        
        # Trade Verdict
        st.markdown("### 🏛️ Executive Trade Verdict")
        if net_vorp_shift >= 15.0:
            st.success(f"🔥 **SMASH ACCEPT:** This trade adds **+{round(net_vorp_shift, 1)} net VORP** to your team! Major value win.")
        elif net_vorp_shift >= 0.0:
            st.info(f"✅ **SLIGHT WIN / FAIR DEAL:** Adds **+{round(net_vorp_shift, 1)} net VORP**. Solid move.")
        elif net_vorp_shift >= -15.0:
            st.warning(f"⚠️ **SLIGHT LOSS:** Costs you **{round(net_vorp_shift, 1)} net VORP**. Only accept if consolidating depth for an elite top-tier starter.")
        else:
            st.error(f"❌ **HARD DECLINE:** This trade drains **{round(net_vorp_shift, 1)} net VORP** from your team. Walk away.")
            
        st.markdown("---")
        
        # Breakdown Tables
        col_tb1, col_tb2 = st.columns(2)
        with col_tb1:
            st.markdown("##### Outgoing Asset Breakdown")
            if not df_give.empty:
                st.dataframe(df_give[['Player', 'Pos_RK', 'FPS', 'True_VORP', 'FP_Rank', 'Rank_Surplus']], use_container_width=True)
            if give_picks:
                st.caption(f"Outgoing Draft Picks: {', '.join(give_picks)} (Total Pick VORP: {round(give_pick_vorp, 1)})")
                
        with col_tb2:
            st.markdown("##### Incoming Asset Breakdown")
            if not df_get.empty:
                st.dataframe(df_get[['Player', 'Pos_RK', 'FPS', 'True_VORP', 'FP_Rank', 'Rank_Surplus']], use_container_width=True)
            if get_picks:
                st.caption(f"Incoming Draft Picks: {', '.join(get_picks)} (Total Pick VORP: {round(get_pick_vorp, 1)})")