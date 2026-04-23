import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE AI Quant", layout="wide")

st.title("🛡️ Institutional Intelligence (NEPSE)")

fetcher = NepseFetcher()
engine = InstitutionalEngine()

# 1. Fetch & Analyze
raw_data = fetcher.get_live_data()
data = engine.apply_metrics(raw_data)

if not data.empty:
    avg_amihud = data['amihud'].median()
    
    # 2. Process Signals
    summaries = [SignalLab.get_summary(row, avg_amihud) for _, row in data.iterrows()]
    res_df = pd.DataFrame(summaries)
    
    tab1, tab2 = st.tabs(["🎯 Trade Advice", "🔬 Deep Quant Data"])
    
    with tab1:
        # SAFETY CHECK: Only filter if 'Action' exists in columns
        if not res_df.empty and 'Action' in res_df.columns:
            logic_df = res_df[res_df['Action'] != "NEUTRAL"].sort_values(by='Confidence', ascending=False)
            
            if not logic_df.empty:
                st.dataframe(logic_df, use_container_width=True, hide_index=True)
            else:
                st.info("No institutional patterns detected in the last few minutes.")
        else:
            st.warning("Waiting for market signals...")

    with tab2:
        st.dataframe(data.sort_values(by='turnover', ascending=False), use_container_width=True)
else:
    st.error("⚠️ Error: No data fetched. Please ensure the NEPSE market is open (11 AM - 3 PM).")
