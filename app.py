import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Pro Official", layout="wide")

# Persistent data to handle "Off-Market" hours
if 'last_valid_data' not in st.session_state:
    st.session_state.last_valid_data = pd.DataFrame()

fetcher = NepseFetcher()
engine = InstitutionalEngine()

st.title("🏛️ NEPSE Official Source Intelligence")

if st.button("🔄 Refresh Official Data"):
    with st.spinner("Handshaking with NEPSE Servers..."):
        raw_df = fetcher.get_live_data()
        
        if not raw_df.empty:
            processed_df = engine.apply_metrics(raw_df)
            st.session_state.last_valid_data = processed_df
            st.success("Data synchronized with official NOTS API.")
        else:
            st.warning("Market is Closed. Showing last recorded session data.")

# Display Logic
if not st.session_state.last_valid_data.empty:
    data = st.session_state.last_valid_data
    avg_amihud = data['amihud'].median()
    
    tab1, tab2 = st.tabs(["🎯 Trade Advice", "📊 Market Depth"])
    
    with tab1:
        summaries = [SignalLab.get_summary(row, avg_amihud) for _, row in data.iterrows()]
        res_df = pd.DataFrame(summaries)
        
        # Actionable filter
        action_df = res_df[res_df['Action'] != "WAIT"].sort_values(by='Confidence', ascending=False)
        st.dataframe(action_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.dataframe(data.sort_values(by='turnover', ascending=False), use_container_width=True)
else:
    st.info("Please click 'Refresh' to pull the latest market session.")
    
