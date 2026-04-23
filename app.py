import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Institutional", layout="wide")

fetcher = NepseFetcher()
engine = InstitutionalEngine()

st.title("🛡️ NEPSE Institutional Intelligence")

# 1. Fetch & Analyze
raw_data = fetcher.get_live_data()
data = engine.apply_metrics(raw_data)
avg_amihud = data['amihud'].median()

# 2. Fix the NameError: Initialize summary_list properly
summary_list = []

for _, row in data.iterrows():
    # Pass metrics to SignalLab
    res = SignalLab.get_summary(row, avg_amihud)
    if res['Signal'] != "NEUTRAL":
        summary_list.append(res)

# 3. Create DataFrame Safely
if len(summary_list) > 0:
    summary_df = pd.DataFrame(summary_list)
else:
    # Empty DataFrame with correct columns to avoid crashes
    summary_df = pd.DataFrame(columns=['Symbol', 'Signal', 'Target', 'StopLoss', 'Insight'])

# 4. Display UI
tab1, tab2 = st.tabs(["🎯 Signals", "📋 Raw Analysis"])

with tab1:
    if not summary_df.empty:
        st.dataframe(summary_df, use_container_width=True)
        # Detailed Expanders
        for _, sig in summary_df.iterrows():
            with st.expander(f"View Plan for {sig['Symbol']}"):
                st.write(f"**Action:** {sig['Signal']} | **Reason:** {sig['Insight']}")
                st.write(f"🎯 Target: {sig['Target']} | 🛡️ SL: {sig['StopLoss']}")
    else:
        st.info("No institutional activity detected right now.")

with tab2:
    st.dataframe(data, use_container_width=True)
    
