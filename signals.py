class SignalLab:
    @staticmethod
    def get_summary(row, mkt_amihud):
        score = 0
        reasons = []

        # Logic A: Big Money Clustering
        if row['is_institutional']:
            score += 45
            reasons.append("Institutional Flow")

        # Logic B: Absorption (High Volume + Low Price Impact)
        if row['rvol'] > 2.0 and row['amihud'] < mkt_amihud:
            score += 30
            reasons.append("Liquidity Absorption")

        # Logic C: Bullish Momentum
        if row['ltp'] > row['open']:
            score += 25
            reasons.append("Bullish Trend")

        # Action Verdict
        action = "WAIT"
        if score >= 70: action = "STRONG BUY"
        elif score >= 45: action = "BUY"
        elif row['ltp'] < row['open'] * 0.97 and row['is_institutional']: action = "EXIT/SELL"

        target = round(row['ltp'] * 1.12, 1)
        sl = round(row['ltp'] * 0.95, 1)

        # Advice Text
        advice_map = {
            "STRONG BUY": f"🔥 Institutional accumulation detected. High probability move. Target: {target}.",
            "BUY": f"✅ Good risk/reward. Smart money is supporting this level. Target: {target}.",
            "EXIT/SELL": "⚠️ Large players are exiting. High risk of drop. Protect capital.",
            "WAIT": "⏳ Retail noise only. No clear institutional footprint."
        }

        return {
            'Symbol': row['symbol'],
            'Action': action,
            'Advice': advice_map[action],
            'Confidence': f"{score}%",
            'Logic': " + ".join(reasons) if reasons else "Neutral"
        }
        
