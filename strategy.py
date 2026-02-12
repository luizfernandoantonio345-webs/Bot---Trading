import json
import os
from indicators import ema, atr
from strategy_config import (
    DECISION_WEIGHTS,
    ENABLE_ADAPTIVE_BIAS,
    MIN_TRADES_FOR_ADAPTATION,
    ADAPT_STEP,
    MAX_SCORE_ADJUST
)

# =============================
# ARQUIVO DE ESTADO
# =============================
STATE_FILE = "strategy_state.json"


# =============================
# ESTADO BASE (NUNCA QUEBRA)
# =============================
BASE_STATE = {
    "stats": {
        "BUY": {"wins": 0, "loss": 0},
        "SELL": {"wins": 0, "loss": 0}
    },
    "bias_adjust": {
        "BUY": 0,
        "SELL": 0
    }
}


# =============================
# LOAD / SAVE (COM MIGRAÇÃO)
# =============================
def load_state():
    if not os.path.exists(STATE_FILE):
        save_state(BASE_STATE)
        return BASE_STATE.copy()

    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        save_state(BASE_STATE)
        return BASE_STATE.copy()

    # 🔧 GARANTE COMPATIBILIDADE
    if "stats" not in data:
        data["stats"] = BASE_STATE["stats"]
    if "bias_adjust" not in data:
        data["bias_adjust"] = BASE_STATE["bias_adjust"]

    save_state(data)
    return data


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


state = load_state()
stats = state["stats"]
bias_adjust = state["bias_adjust"]


# =============================
# MOTOR DE DECISÃO
# =============================
def calcular_decisao(contexto):
    score_buy = 0
    score_sell = 0

    # Tendência
    if contexto["trend"] == "ALTA":
        score_buy += DECISION_WEIGHTS["trend"] * 100
    else:
        score_sell += DECISION_WEIGHTS["trend"] * 100

    # Pullback
    if contexto["pullback"]:
        score_buy += DECISION_WEIGHTS["pullback"] * 100
        score_sell += DECISION_WEIGHTS["pullback"] * 100

    # Candle
    if contexto["candle_forca"] == "BUY":
        score_buy += DECISION_WEIGHTS["candle"] * 100
    elif contexto["candle_forca"] == "SELL":
        score_sell += DECISION_WEIGHTS["candle"] * 100

    # Sessão
    if contexto["sessao"] in ["LONDRES", "NY"]:
        score_buy += DECISION_WEIGHTS["session"] * 100
        score_sell += DECISION_WEIGHTS["session"] * 100

    # ATR
    if contexto["atr_ok"]:
        score_buy += DECISION_WEIGHTS["atr"] * 100
        score_sell += DECISION_WEIGHTS["atr"] * 100

    # Bias aprendido
    if ENABLE_ADAPTIVE_BIAS:
        score_buy += bias_adjust["BUY"]
        score_sell += bias_adjust["SELL"]

    total = score_buy + score_sell
    prob_buy = round((score_buy / total) * 100, 1)
    prob_sell = round((score_sell / total) * 100, 1)

    confianca = "ALTA" if abs(prob_buy - prob_sell) >= 10 else "MEDIA"
    recomendacao = "BUY" if prob_buy > prob_sell else "SELL"

    return prob_buy, prob_sell, recomendacao, confianca


# =============================
# AVALIADOR INTERNO (DEBUG / BACKTEST)
# =============================
def avaliar_setup(df_m15, df_h1):
    df_h1["ema200"] = ema(df_h1["close"], 200)
    df_m15["ema50"] = ema(df_m15["close"], 50)
    df_m15["atr"] = atr(df_m15)

    close = float(df_m15["close"].iloc[-1])
    ema50 = float(df_m15["ema50"].iloc[-1])
    ema200 = float(df_h1["ema200"].iloc[-1])
    atr_val = float(df_m15["atr"].iloc[-1])

    if close > ema200:
        direcao = "BUY"
        tendencia = "ALTA"
    elif close < ema200:
        direcao = "SELL"
        tendencia = "BAIXA"
    else:
        return None

    if abs(close - ema50) > atr_val * 0.5:
        return None

    score = min(80 if atr_val > 0 else 70, 100)

    return {
        "direcao": direcao,
        "tendencia": tendencia,
        "pullback": True,
        "atr": atr_val,
        "score": score
    }


# =============================
# APRENDIZADO (CHAMADO NO FECHAMENTO)
# =============================
def atualizar_resultado(direcao, ganhou):
    stats[direcao]["wins" if ganhou else "loss"] += 1

    total = (
        stats["BUY"]["wins"] + stats["BUY"]["loss"] +
        stats["SELL"]["wins"] + stats["SELL"]["loss"]
    )

    if total >= MIN_TRADES_FOR_ADAPTATION:
        buy_wr = stats["BUY"]["wins"] / max(1, stats["BUY"]["wins"] + stats["BUY"]["loss"])
        sell_wr = stats["SELL"]["wins"] / max(1, stats["SELL"]["wins"] + stats["SELL"]["loss"])

        if buy_wr > sell_wr:
            bias_adjust["BUY"] = min(bias_adjust["BUY"] + ADAPT_STEP, MAX_SCORE_ADJUST)
            bias_adjust["SELL"] = max(bias_adjust["SELL"] - ADAPT_STEP, -MAX_SCORE_ADJUST)
        else:
            bias_adjust["SELL"] = min(bias_adjust["SELL"] + ADAPT_STEP, MAX_SCORE_ADJUST)
            bias_adjust["BUY"] = max(bias_adjust["BUY"] - ADAPT_STEP, -MAX_SCORE_ADJUST)

    save_state(state)
