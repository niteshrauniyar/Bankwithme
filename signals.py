class SignalLab:
    @staticmethod
    def get_summary(row, market_avg_amihud):
        # Scoring logic based on research features
        score = 0
        reasons = []

        # 3.1 Order Splitting (Volume spike + Inst cluster)
        if row['is_institutional'] and row['volume'] > 10000:
            score += 40
            reasons.append("Big Player activity (Cluster Detected)")

        # 3.2 Informed Trading (High Centrality + Low Amihud)
        if row['market_centrality'] > 1.0 and row['amihud'] < market_avg_amihud:
            score += 30
            reasons.append("Informed trading signature (High Influence)")

        # Decision
        verdict = "NEUTRAL"
        if score >= 60: verdict = "STRONG BUY"
        elif score >= 40: verdict = "BUY"
        elif row['ltp'] < row['open'] * 0.98 and row['is_institutional']: verdict = "DISTRIBUTION (SELL)"

        # Target & SL (Institutional Ranges)
        entry = row['ltp']
        target = round(entry * 1.10, 2) # Institutional target usually 10%
        sl = round(entry * 0.95, 2)

        # Simple Words explanation
        if verdict == "STRONG BUY":
            explanation = f"YES: Institutional accumulation detected. Large orders are being split to hide entry. Target: Rs. {target}."
        elif verdict == "BUY":
            explanation = f"WATCH: Big players are active. Good entry near {entry}. Target: Rs. {target}."
        elif verdict == "DISTRIBUTION (SELL)":
            explanation = f"NO: Large players are exiting their positions. High selling pressure. Support at Rs. {sl}."
        else:
            explanation = "RETAIL NOISE: No clear big player footprint. Better to wait."

        return {
            'Symbol': row['symbol'],
            'Signal': verdict,
            'Target': target,
            'StopLoss': sl,
            'Insight': " | ".join(reasons) if reasons else "Retail Activity",
            'SimpleSummary': explanation
        }
        
