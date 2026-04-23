import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Pro Intelligence", layout="wide")

# Init classes
fetcher = NepseFetcher()
engine = InstitutionalEngine()

st.title("📊 NEPSE Institutional Trade Engine")

# Fetch and Process
with st.spinner('Scanning Live Market Flow...'):
    raw_data = fetcher.get_live_data()
    data = engine.apply_metrics(raw_data)

if not data.empty:
    avg_amihud = data['amihud'].median()
    
    tab1, tab2 = st.tabs(["🎯 AI Signals & Advice", "🔬 Technical Matrix"])
    
    with tab1:
        summaries = [SignalLab.get_summary(row, avg_amihud) for _, row in data.iterrows()]
        res_df = pd.DataFrame(summaries)
        
        # Display only relevant signals
        logic_df = res_df[res_df['Action'] != "NEUTRAL"].sort_values(by='Confidence', ascending=False)
        if not logic_df.empty:
            st.dataframe(logic_df, use_container_width=True, hide_index=True)
        else:
            st.info("The market is currently quiet. No institutional breakouts detected.")

    with tab2:
        st.dataframe(data.sort_values(by='turnover', ascending=False), use_container_width=True)
else:
    st.error("Data refresh failed. Please check your internet or site source.")
    
