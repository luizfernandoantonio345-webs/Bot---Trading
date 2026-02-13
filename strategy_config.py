# strategy_config.py
# =============================
# CONFIGURAÇÃO CENTRAL DA STRATEGY
# =============================

# modo de adaptação
ENABLE_ADAPTIVE_BIAS = True

# pesos do motor de decisão (somam 1.0)
DECISION_WEIGHTS = {
    "trend": 0.40,
    "pullback": 0.25,
    "candle": 0.15,
    "session": 0.10,
    "atr": 0.10
}

# adaptação
MIN_TRADES_FOR_ADAPTATION = 30
ADAPT_STEP = 2
MAX_SCORE_ADJUST = 6

# =============================
# SEMI-AGRESSIVO (CONTROLADO)
# =============================

ENABLE_SEMI_AGGRESSIVE = True

# score mínimo
MIN_SCORE_AUTO_SEMI = 78
MIN_SCORE_MANUAL_SEMI = 70

# mercado vivo
ATR_LIVE_FACTOR = 0.7   # 70% da média recente
ATR_LOOKBACK = 20       # candles M15
