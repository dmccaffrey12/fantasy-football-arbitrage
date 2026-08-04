import streamlit as st
import pandas as pd
import numpy as np

def get_pick_vorp_estimate(pick_num, df_calc):
    """Estimates the True VORP yield of a specific draft pick slot based on the projection board."""
    if df_calc is None or df_calc.empty:
        return 0.0
    
    idx = max(0, min(int(pick_num) - 1, len(df_calc) - 1))
    return float(df_calc.iloc[idx]['True_VORP'])

def render_trade_analyzer(df_calc, df_undrafted, run_monte_carlo_sims_func):
    st.header("🤝 Preseason Blockbuster Trade & Draft Pick Analyzer")
    st.caption("Evaluate large multi-player (up to 5-for-5) and draft pick trade offers based on Custom VORP, Roster Drop Penalties & Market Perception.")
    
    if df_calc is None or df_calc.empty:
        st.error("No projection data available to analyze trades.")
        return

    all_players = ["-- None --"] + df_calc['Player'].tolist()
    all_picks = [f"Round {((i-1)//12)+1}, Pick {((i-1)%12)+1} (Overall #{i})" for i in range(1, 181)]
    
    col_give, col_get = st.columns(2)
    
    # --- LEFT SIDE: YOU GIVE (OUTGOING) ---
    with col_give:
        st.subheader("📤 You Give (Outgoing)")
        
        with st.expander("👤 Outgoing Players (Up to 5 Slots)", expanded=True):
            give_p1 = st.selectbox("Outgoing Player 1", all_players, key="g_p1")
            give_p2 = st.selectbox("Outgoing Player 2", all_players, key="g_p2")
            give_p3 = st.selectbox("Outgoing Player 3", all_players, key="g_p3")
            give_p4 = st.selectbox("Outgoing Player 4", all_players, key="g_p4")
            give_p5 = st.selectbox("Outgoing Player 5", all_players, key="g_p5")
            
        with st.expander("🎟️ Outgoing Draft Picks", expanded=False):
            give_picks = st.multiselect(
                "Select Outgoing Draft Picks",
                all_picks,
                key="g_picks"
            )

    # --- RIGHT SIDE: YOU RECEIVE (INCOMING) ---
    with col_get:
        st.subheader("📥 You Receive (Incoming)")
        
        with st.expander("👤 Incoming Players (Up to 5 Slots)", expanded=True):
            get_p1 = st.selectbox("Incoming Player 1", all_players, key="rec_p1")
            get_p2 = st.selectbox("Incoming Player 2", all_players, key="rec_p2")
            get_p3 = st.selectbox("Incoming Player 3", all_players, key="rec_p3")
            get_p4 = st.selectbox("Incoming Player 4", all_players, key="rec_p4")
            get_p5 = st.selectbox("Incoming Player 5", all_players, key="rec_p5")
            
        with st.expander("🎟️ Incoming Draft Picks", expanded=False):
            get_picks = st.multiselect(
                "Select Incoming Draft Picks",
                all_picks,
                key="rec_picks"
            )

    # Compile non-empty selections
    give_players = [p for p in [give_p1, give_p2, give_p3, give_p4, give_p5] if p != "-- None --"]
    get_players = [p for p in [get_p1, get_p2, get_p3, get_p4, get_p5] if p != "-- None --"]

    st.markdown("---")
    
    if give_players or get_players or give_picks or get_picks:
        df_give = df_calc[df_calc['Player'].isin(give_players)].copy()
        df_get = df_calc[df_calc['Player'].isin(get_players)].copy()
        
        # Calculate Outgoing Values
        give_player_fps = df_give['FPS'].sum() if not df_give.empty else 0.0
        give_player_vorp = df_give['True_VORP'].sum() if not df_give.empty else 0.0
        
        # Calculate Incoming Values
        get_player_fps = df_get['FPS'].sum() if not df_get.empty else 0.0
        get_player_vorp = df_get['True_VORP'].sum() if not df_get.empty else 0.0
        
        # Calculate Pick Values
        give_pick_vorp = sum([get_pick_vorp_estimate(int(p.split("Overall #")[1].replace(")", "")), df_calc) for p in give_picks])
        get_pick_vorp = sum([get_pick_vorp_estimate(int(p.split("Overall #")[1].replace(")", "")), df_calc) for p in get_picks])
        
        total_give_vorp = give_player_vorp + give_pick_vorp
        total_get_vorp = get_player_vorp + get_pick_vorp
        
        # Roster Slot Balancing for Uneven Blockbusters
        slot_diff = len(give_players) - len(get_players)
        slot_adjustment = 0.0
        
        if slot_diff > 0:
            replacement_val = df_undrafted.iloc[min(10, len(df_undrafted)-1)]['True_VORP'] if not df_undrafted.empty else 0.0
            slot_adjustment = slot_diff * replacement_val
            st.info(f"💡 **Roster Slot Advantage:** Giving **{len(give_players)}** players and receiving **{len(get_players)}** opens **{slot_diff}** bench slot(s). Adding **+{round(slot_adjustment, 1)} VORP** for replacement-level waiver pickups.")
        elif slot_diff < 0:
            replacement_val = df_undrafted.iloc[min(10, len(df_undrafted)-1)]['True_VORP'] if not df_undrafted.empty else 0.0
            slot_adjustment = slot_diff * replacement_val
            st.warning(f"⚠️ **Roster Slot Penalty:** Receiving **{len(get_players)}** players and giving **{len(give_players)}** forces **{abs(slot_diff)}** roster drop(s). Deducting **{round(slot_adjustment, 1)} VORP** for lost roster flexibility.")
            
        adjusted_get_vorp = total_get_vorp + slot_adjustment
        net_vorp_shift = adjusted_get_vorp - total_give_vorp
        net_fps_shift = get_player_fps - give_player_fps
        
        # Display Core Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Outgoing Total VORP", round(total_give_vorp, 1))
        m2.metric("Incoming Total VORP", round(total_get_vorp, 1))
        m3.metric("Net Projected Points Δ", f"{'+' if net_fps_shift >= 0 else ''}{round(net_fps_shift, 1)}")
        m4.metric(
            "Net True VORP Δ", 
            f"{'+' if net_vorp_shift >= 0 else ''}{round(net_vorp_shift, 1)}",
            delta=f"{round(net_vorp_shift, 1)} VORP",
            delta_color="normal" if net_vorp_shift >= 0 else "inverse"
        )
        
        # Executive Trade Verdict
        st.markdown("### 🏛️ Executive Blockbuster Verdict")
        if net_vorp_shift >= 20.0:
            st.success(f"🔥 **SMASH ACCEPT:** This trade adds **+{round(net_vorp_shift, 1)} net VORP** to your roster! Major value windfall.")
        elif net_vorp_shift >= 0.0:
            st.info(f"✅ **SLIGHT WIN / FAIR DEAL:** Adds **+{round(net_vorp_shift, 1)} net VORP**. Solid move.")
        elif net_vorp_shift >= -20.0:
            st.warning(f"⚠️ **SLIGHT LOSS:** Costs you **{round(net_vorp_shift, 1)} net VORP**. Only accept if consolidating depth for an elite top-tier starter.")
        else:
            st.error(f"❌ **HARD DECLINE:** This trade drains **{round(net_vorp_shift, 1)} net VORP** from your team. Walk away.")
            
        st.markdown("---")
        
        # Asset Breakdown Tables
        col_tb1, col_tb2 = st.columns(2)
        with col_tb1:
            st.markdown(f"##### Outgoing Assets ({len(give_players)} Players, {len(give_picks)} Picks)")
            if not df_give.empty:
                st.dataframe(df_give[['Player', 'Pos_RK', 'FPS', 'True_VORP', 'FP_Rank', 'Rank_Surplus']], use_container_width=True)
            if give_picks:
                st.caption(f"Outgoing Picks: {', '.join(give_picks)} (Total Pick VORP: {round(give_pick_vorp, 1)})")
                
        with col_tb2:
            st.markdown(f"##### Incoming Assets ({len(get_players)} Players, {len(get_picks)} Picks)")
            if not df_get.empty:
                st.dataframe(df_get[['Player', 'Pos_RK', 'FPS', 'True_VORP', 'FP_Rank', 'Rank_Surplus']], use_container_width=True)
            if get_picks:
                st.caption(f"Incoming Picks: {', '.join(get_picks)} (Total Pick VORP: {round(get_pick_vorp, 1)})")