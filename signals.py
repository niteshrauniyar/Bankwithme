class SignalLab:
    @staticmethod
    def get_summary(row, market_median_amihud):
        score = 0
        factors = []

        # Logic 1: Smart Money Cluster
        if row['is_institutional']:
            score += 40
            factors.append("Institutional Clustering")

        # Logic 2: Absorption (High Vol + Low Price Impact)
        if row['rvol'] > 2.0 and row['amihud'] < market_median_amihud:
            score += 30
            factors.append("Liquidity Absorption")

        # Logic 3: Trend Confirmation
        if row['ltp'] > row['open']:
            score += 20
            factors.append("Bullish Impulse")

        # Classification
        verdict = "WAIT"
        if score >= 70: verdict = "STRONG BUY"
        elif score >= 40: verdict = "BUY"
        elif row['ltp'] < row['open'] * 0.98 and row['is_institutional']: verdict = "SELL / EXIT"

        # Trading Levels
        entry = row['ltp']
        target = round(entry * 1.12, 1) # 12% target
        sl = round(entry * 0.95, 1)    # 5% stop loss

        # Simple Words logic
        if verdict == "STRONG BUY":
            summary = f"YES: High institutional conviction. Smart money is absorbing supply. Target Rs. {target}."
        elif verdict == "BUY":
            summary = f"WATCH: Accumulation detected. Price looks efficient for entry. Target Rs. {target}."
        elif verdict == "SELL / EXIT":
            summary = "NO: Institutional distribution (selling) detected. Avoid or exit current position."
        else:
            summary = "NEUTRAL: Retail noise. No clear big player footprint."

        return {
            'Symbol': row['symbol'],
            'Signal': verdict,
            'Confidence': f"{score}%",
            'Target': target,
            'StopLoss': sl,
            'Analysis': " + ".join(factors) if factors else "No Institutional Activity",
            'SimpleAdvice': summary
        }
        
