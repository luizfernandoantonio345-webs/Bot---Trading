# ==========================================================
# SCORE DE MERCADO (0–100)
# AVALIA QUALIDADE DO CONTEXTO
# NÃO DECIDE ENTRADA
# NÃO BLOQUEIA OPERAÇÃO
# ==========================================================

from datetime import datetime


# ----------------------------------------------------------
# SESSÃO DE MERCADO (UTC)
# ----------------------------------------------------------
def sessao_favoravel():
    """
    Retorna True se estiver em sessão favorável
    Londres / Nova York
    """
    hora_utc = datetime.utcnow().hour

    # Londres: 07–16 UTC
    # NY:      12–21 UTC
    if 7 <= hora_utc <= 21:
        return True
    return False


# ----------------------------------------------------------
# FORÇA DO CANDLE
# ----------------------------------------------------------
def candle_forte(open_, high, low, close):
    """
    Avalia se o candle tem corpo relevante
    """
    range_total = high - low
    if range_total <= 0:
        return False

    corpo = abs(close - open_)
    proporcao = corpo / range_total

    return proporcao >= 0.6  # candle forte ≥60% do range


# ----------------------------------------------------------
# SCORE PRINCIPAL
# ----------------------------------------------------------
def calcular_score(
    *,
    tendencia_ok: bool,
    pullback_ok: bool,
    atr_val: float,
    distancia_ema: float,
    candle_open: float,
    candle_high: float,
    candle_low: float,
    candle_close: float
):
    """
    Retorna:
    score (int 0–100)
    motivos (list[str])
    """

    score = 0
    motivos = []

    # ---------------------------
    # TENDÊNCIA (30 pts)
    # ---------------------------
    if tendencia_ok:
        score += 30
        motivos.append("Tendência clara (EMA200 H1)")

    # ---------------------------
    # PULLBACK (25 pts)
    # ---------------------------
    if pullback_ok:
        score += 25
        motivos.append("Pullback saudável (EMA50 M15)")

    # ---------------------------
    # VOLATILIDADE ATR (15 pts)
    # ---------------------------
    if atr_val and atr_val > 0:
        score += 15
        motivos.append("ATR válido")

    # ---------------------------
    # DISTÂNCIA DA EMA (10 pts)
    # ---------------------------
    if atr_val and atr_val > 0:
        if distancia_ema >= atr_val * 0.25:
            score += 10
            motivos.append("Distância ideal da EMA")
        elif distancia_ema >= atr_val * 0.1:
            score += 5
            motivos.append("Pullback aceitável")

    # ---------------------------
    # CANDLE FORTE (10 pts)
    # ---------------------------
    if candle_forte(
        candle_open,
        candle_high,
        candle_low,
        candle_close
    ):
        score += 10
        motivos.append("Candle forte")

    # ---------------------------
    # SESSÃO DE MERCADO (10 pts)
    # ---------------------------
    if sessao_favoravel():
        score += 10
        motivos.append("Sessão favorável (Londres/NY)")

    # ---------------------------
    # NORMALIZAÇÃO
    # ---------------------------
    score = min(score, 100)

    return score, motivos
