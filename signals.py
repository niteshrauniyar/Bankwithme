class SignalLab:
    @staticmethod
    def get_advice(row):
        score = 0
        if row['is_institutional']: score += 50
        if row['ltp'] > row['open']: score += 30
        if row['amihud'] < 0.5: score += 20 # Low price impact despite volume
        
        verdict = "WAIT"
        if score >= 80: verdict = "STRONG BUY"
        elif score >= 50: verdict = "BUY"
        elif row['change_pct'] < -3 and row['is_institutional']: verdict = "SELL"
        
        target = round(row['ltp'] * 1.10, 2)
        sl = round(row['ltp'] * 0.95, 2)

        return {
            'Symbol': row['symbol'],
            'Action': verdict,
            'Confidence': f"{score}%",
            'Target': target,
            'StopLoss': sl,
            'Reason': "Institutional Entry" if score >= 50 else "Retail Movement"
        }
        
