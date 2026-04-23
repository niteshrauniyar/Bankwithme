class SignalLab:
    @staticmethod
    def get_summary(row, market_avg_amihud):
        score = 0
        verdict = "NEUTRAL"
        reasons = []

        # Logic: Accumulation
        if row['is_institutional'] and row['ltp'] > row['open']:
            score += 40
            reasons.append("Institutional Accumulation")
        
        # Logic: Absorption (Price not moving much despite big volume)
        if row['vol_intensity'] > 2.0 and row['amihud'] < market_avg_amihud:
            score += 30
            reasons.append("Big Player Absorption")

        if score >= 60: verdict = "STRONG BUY"
        elif score >= 40: verdict = "BUY"
        elif row['ltp'] < row['open'] * 0.98 and row['is_institutional']: verdict = "DANGER: SELL"

        target = round(row['ltp'] * 1.12, 1) if "BUY" in verdict else 0.0
        sl = round(row['ltp'] * 0.94, 1)

        # Simple Words Explanation
        if verdict == "STRONG BUY":
            explanation = f"YES: Big money is entering. Buy near {row['ltp']}. Target Rs. {target}."
        elif verdict == "DANGER: SELL":
            explanation = f"NO: Institutional distribution (selling) detected. Protect capital. Exit."
        else:
            explanation = "WAIT: No clear footprint from the 'Big Players' right now."

        return {
            'Symbol': row['symbol'],
            'Action': verdict,
            'Advice': explanation,
            'Target': target,
            'SL': sl,
            'Confidence': f"{score}%"
        }
        
