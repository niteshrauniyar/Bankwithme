class SignalLab:
    @staticmethod
    def get_summary(row, df_stats):
        score = 0
        reasons = []
        
        # Logic A: Institutional Accumulation
        if row['is_institutional'] and row['ltp'] > row['open']:
            score += 45
            reasons.append("Institutional Accumulation Detected")

        # Logic B: Liquidity Absorption (Low Amihud + High Volume)
        if row['amihud'] < df_stats['amihud_median'] and row['rvol'] > 1.5:
            score += 25
            reasons.append("Efficient Absorption (Smart Money Buying)")

        # Logic C: Order Flow Persistence (Metaorder Signature)
        if row['rvol'] > 3.0:
            score += 20
            reasons.append("Heavy Order Flow (Metaorder Signature)")

        # Logic D: Volatility Warning
        if row['volatility_regime'] == "HIGH":
            score -= 10 # Deduct for high risk

        # Final Classification
        verdict = "WAIT"
        if score >= 70: verdict = "STRONG BUY"
        elif score >= 40: verdict = "BUY"
        elif row['ltp'] < row['open'] * 0.97 and row['is_institutional']: verdict = "INSTITUTIONAL DUMP (SELL)"

        # Target Pricing
        entry = row['ltp']
        target = round(entry * 1.15 if verdict == "STRONG BUY" else entry * 1.08, 2)
        sl = round(entry * 0.94, 2)

        return {
            'Symbol': row['symbol'],
            'Signal': verdict,
            'Target': target,
            'StopLoss': sl,
            'Confidence': f"{score}%",
            'Logic': " | ".join(reasons) if reasons else "Retail Noise",
            'SimpleSummary': SignalLab._generate_text(verdict, target, score)
        }

    @staticmethod
    def _generate_text(verdict, target, score):
        if verdict == "STRONG BUY":
            return f"🔥 HIGH CONVICTION: Institutions are aggressively entering. Strong probability of trend continuation to {target}."
        if verdict == "BUY":
            return f"✅ SMART ENTRY: Big players are active. Good risk/reward ratio. Target: {target}."
        if verdict == "INSTITUTIONAL DUMP (SELL)":
            return "⚠️ ALERT: Large players are exiting. High probability of a sharp drop. Protect capital."
        return "⏳ NEUTRAL: Not enough institutional footprint. Avoid unnecessary exposure."
