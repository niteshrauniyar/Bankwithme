import streamlit as st
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Pro Quant", layout="wide")

fetcher = NepseFetcher()
engine = InstitutionalEngine()

st.title("🛡️ Institutional Intelligence System (NEPSE)")
st.write("Detecting Metaorders, Amihud Illiquidity & Smart Money Clusters")

# Fetch and Process
data = fetcher.get_live_data()
data = engine.apply_metrics(data)
avg_amihud = data['amihud'].median()

# Layout
tab1, tab2 = st.tabs(["📊 Market Intelligence", "🤖 AI Trade Summary"])

with tab1:
    st.subheader("Microstructure Analysis")
    # Show key academic metrics
    st.dataframe(data[['symbol', 'ltp', 'amihud', 'kyle_lambda', 'is_institutional']], use_container_width=True)

with tab2:
    st.subheader("High-Conviction Institutional Setups")
    
    # Generate Summaries
    summary_list = []
    for _, row in data.iterrows():
        summary = SignalLab.get_summary(row, avg_amihud)
        if summary['Signal'] != "NEUTRAL":
            summary_list.append(summary)
    
    if summary_list:
        summary_df = pd.DataFrame(summary_list)
        for _, sig in summary_df.iterrows():
            with st.expander(f"📌 {sig['Symbol']} - {sig['Signal']}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Target Price", sig['Target'])
                col2.metric("Stop Loss", sig['StopLoss'])
                col3.write(f"**Quant Insight:** {sig['Insight']}")
                
                # Simple words logic
                st.info(f"**Summary:** Big players are likely active in {sig['Symbol']}. The {sig['Insight'].lower()} indicates institutional strength. Trade with caution at target {sig['Target']}.")
    else:
        st.write("No high-conviction institutional setups detected in the current session.")

st.sidebar.markdown("### Research Framework")
st.sidebar.info("""
- **Amihud Ratio:** Measures price efficiency.
- **Kyle's Lambda:** Measures market impact.
- **ML Clustering:** Separates metaorders from retail noise.
""")
