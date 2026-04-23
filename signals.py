class SignalLab:
    @staticmethod
    def get_summary(row, mkt_amihud):
        score = 0
        reasons = []

        if row['is_institutional']:
            score += 45
            reasons.append("Institutional Flow")
        
        if row['rvol'] > 2.5 and row['amihud'] < mkt_amihud:
            score += 35
            reasons.append("High Absorption (Big Money)")

        if row['ltp'] > row['open']:
            score += 20
            reasons.append("Bullish Day Trend")

        # Verdict logic
        action = "WAIT"
        if score >= 75: action = "STRONG BUY"
        elif score >= 45: action = "BUY"
        elif row['ltp'] < row['open'] * 0.97 and row['is_institutional']: action = "EXIT / SELL"

        target = round(row['ltp'] * 1.15, 1) if "BUY" in action else 0
        
        # Simple Advice text
        advice = {
            "STRONG BUY": f"🔥 YES: High institutional volume. Enter now. Target: {target}.",
            "BUY": f"✅ WATCH: Big players are active. Good entry. Target: {target}.",
            "EXIT / SELL": "⚠️ ALERT: Major distribution (selling) by institutions. Exit.",
            "WAIT": "⏳ NEUTRAL: Only retail noise. No big money found."
        }

        return {
            'Symbol': row['symbol'],
            'Verdict': action,
            'SimpleAdvice': advice[action],
            'Confidence': f"{score}%",
            'Logic': " + ".join(reasons) if reasons else "Retail Noise"
        }
