import streamlit as st
import pandas as pd
import numpy as np

def render_trade_analyzer(df_calc, df_undrafted, run_monte_carlo_sims_func):
    st.header("🤝 Preseason & In-Season Trade Arbitrage Analyzer")
    st.caption("Evaluate multi-player trade offers based on Custom VORP, Roster Slot Opportunity Cost & Market Perception.")
    
    if df_calc is None or df_calc.empty:
        st.error("No projection data available to analyze trades.")
        return

    all_players = df_calc['Player'].tolist()
    
    col_give, col_get = st.columns(2)
    
    # --- LEFT SIDE: GIVING AWAY ---
    with col_give:
        st.subheader("📤 You Give (Outgoing)")
        give_players = st.multiselect(
            "Select Player(s) You Send",
            all_players,
            key="trade_give_selector"
        )
        
    # --- RIGHT SIDE: RECEIVING ---
    with col_get:
        st.subheader("📥 You Receive (Incoming)")
        get_players = st.multiselect(
            "Select Player(s) You Receive",
            all_players,
            key="trade_get_selector"
        )
        
    st.markdown("---")
    
    if give_players or get_players:
        df_give = df_calc[df_calc['Player'].isin(give_players)].copy()
        df_get = df_calc[df_calc['Player'].isin(get_players)].copy()
        
        give_fps = df_give['FPS'].sum() if not df_give.empty else 0.0
        give_vorp = df_give['True_VORP'].sum() if not df_give.empty else 0.0
        
        get_fps = df_get['FPS'].sum() if not df_get.empty else 0.0
        get_vorp = df_get['True_VORP'].sum() if not df_get.empty else 0.0
        
        # Slot adjustment for uneven trades (e.g., 2-for-1)
        slot_diff = len(give_players) - len(get_players)
        slot_adjustment = 0.0
        
        if slot_diff > 0:
            # You give more players than you get -> You gain bench slots
            # Free up room for best available undrafted player baseline
            replacement_val = df_undrafted.iloc[min(10, len(df_undrafted)-1)]['True_VORP'] if not df_undrafted.empty else 0.0
            slot_adjustment = slot_diff * replacement_val
            st.info(f"💡 **Roster Slot Advantage:** Receiving fewer players opens **{slot_diff}** roster slot(s). Adding **+{round(slot_adjustment, 1)} VORP** for replacement-level pickup potential.")
        elif slot_diff < 0:
            # You get more players than you give -> You lose bench slots / drop players
            replacement_val = df_undrafted.iloc[min(10, len(df_undrafted)-1)]['True_VORP'] if not df_undrafted.empty else 0.0
            slot_adjustment = slot_diff * replacement_val
            st.warning(f"⚠️ **Roster Slot Penalty:** Receiving more players forces **{abs(slot_diff)}** roster drop(s). Deducting **{round(slot_adjustment, 1)} VORP** for lost roster flexibility.")
            
        adjusted_get_vorp = get_vorp + slot_adjustment
        net_vorp_shift = adjusted_get_vorp - give_vorp
        net_fps_shift = get_fps - give_fps
        
        # Display Core Comparative Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Outgoing Total FPS", round(give_fps, 1))
        m2.metric("Incoming Total FPS", round(get_fps, 1))
        m3.metric("Net Projected Points Δ", f"{'+' if net_fps_shift >= 0 else ''}{round(net_fps_shift, 1)}")
        m4.metric(
            "Net True VORP Δ", 
            f"{'+' if net_vorp_shift >= 0 else ''}{round(net_vorp_shift, 1)}",
            delta=f"{round(net_vorp_shift, 1)} VORP",
            delta_color="normal" if net_vorp_shift >= 0 else "inverse"
        )
        
        # Trade Verdict
        st.markdown("### 🏛️ Executive Trade Verdict")
        if net_vorp_shift >= 15.0:
            st.success(f"🔥 **SMASH ACCEPT:** This trade adds **+{round(net_vorp_shift, 1)} net VORP** to your roster! Major value win.")
        elif net_vorp_shift >= 0.0:
            st.info(f"✅ **SLIGHT WIN / FAIR DEAL:** Adds **+{round(net_vorp_shift, 1)} net VORP**. Good deal if it fills a starting positional need.")
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
        with col_tb2:
            st.markdown("##### Incoming Asset Breakdown")
            if not df_get.empty:
                st.dataframe(df_get[['Player', 'Pos_RK', 'FPS', 'True_VORP', 'FP_Rank', 'Rank_Surplus']], use_container_width=True)