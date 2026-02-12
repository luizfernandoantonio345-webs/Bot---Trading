# risk_config.py

def get_risk_config():
    return {
        "RISK_PER_TRADE": 0.25,
        "MAX_DAILY_RISK": 1.0,
        "DAILY_PROFIT_TARGET": 1.0,
        "MAX_TRADES_PER_DAY": 3,
        "MAX_CONSECUTIVE_LOSSES": 2,
        "REAL_SAFE": True
    }
