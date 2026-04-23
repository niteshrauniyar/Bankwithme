class SignalLab:
    @staticmethod
    def get_summary(row, market_avg_amihud):
        score = 0
        factors = []
        
        # Institutional Detection
        if row['is_institutional']:
            score += 40
            factors.append("Big Money Presence")
        
        # Absorption Check
        if row['rvol'] > 2.0 and row['amihud'] < market_avg_amihud:
            score += 30
            factors.append("Liquidity Absorption")

        # Verdict Logic
        action = "NEUTRAL"
        if score >= 60: action = "STRONG BUY"
        elif score >= 40: action = "BUY"
        elif row['ltp'] < row['open'] * 0.98 and row['is_institutional']: action = "SELL / EXIT"

        target = round(row['ltp'] * 1.10, 1) # Target 10% gain
        sl = round(row['ltp'] * 0.95, 1)    # SL 5% loss

        # "Simple Words" Advice
        if action == "STRONG BUY":
            advice = f"🔥 YES: Big players are buying. Target Rs. {target}. Buy now."
        elif action == "BUY":
            advice = f"✅ WATCH: Accumulation detected. Entry near {row['ltp']} is good."
        elif action == "SELL / EXIT":
            advice = f"⚠️ NO: Institutional dumping detected. Exit/Sell immediately."
        else:
            advice = "⏳ WAIT: No big players active here. Just retail noise."

        return {
            'Symbol': row['symbol'],
            'Action': action,      # This matches your app.py call
            'Advice': advice,
            'Target': target,
            'StopLoss': sl,
            'Confidence': f"{score}%"
        }
