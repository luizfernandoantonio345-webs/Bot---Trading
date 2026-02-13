from datetime import datetime
from discord_alert import enviar_alerta

# =============================
# CONTROLES GLOBAIS
# =============================
ultimo_alerta = {}
ultimo_score = {}

SCORE_DELTA_MIN = 10
SCORE_SOM_MIN = 65
SCORE_SOM_FORTE = 85


# =============================
# SESSÕES
# =============================
def sessao_atual():
    h = datetime.utcnow().hour
    if 7 <= h < 12:
        return "LONDRES"
    elif 12 <= h < 17:
        return "LONDRES/NY"
    elif 17 <= h < 21:
        return "NY"
    else:
        return "FORA"


# =============================
# CLASSIFICAÇÃO
# =============================
def classificar(score):
    if score >= 90:
        return "🔥 IDEAL (AUTO)"
    elif score >= 85:
        return "🚨 FORTE (PRIORIDADE MÁXIMA)"
    elif score >= 75:
        return "🟢 BOA (MANUAL)"
    elif score >= 65:
        return "🔵 ATENÇÃO"
    elif score >= 50:
        return "🟡 FORMAÇÃO"
    else:
        return "🔴 FRACO"


def barra_score(score):
    total = 10
    preenchido = int(score / 10)
    return "█" * preenchido + "░" * (total - preenchido)


# =============================
# EXPECTATIVA
# =============================
def expectativa(score, pullback_ok, pre_pullback):
    if score < 50:
        return "Sem expectativa operacional."
    if score < 60:
        return "Mercado começando a se alinhar."
    if pre_pullback and not pullback_ok:
        return "Pullback provável se houver desaceleração."
    if pullback_ok and score >= 75:
        return "Continuação de tendência favorecida."
    if score >= 90:
        return "Contexto ideal — execução automática."
    return "Acompanhar estrutura e candle."


# =============================
# NOTIFICADOR PRINCIPAL
# =============================
def notificar(
    *,
    symbol,
    direcao,
    score,
    tendencia,
    pullback_ok,
    pre_pullback,
    atr,
    prob_buy=None,
    prob_sell=None,
    recomendacao=None,
    modo=None
):
    global ultimo_alerta, ultimo_score

    sessao = sessao_atual()

    # 🔕 Silenciar fora de sessão
    if sessao == "FORA":
        return

    chave_sessao = f"{symbol}_{direcao}_{sessao}"

    # 📉 Anti-spam por variação real de score
    if chave_sessao in ultimo_score:
        if abs(score - ultimo_score[chave_sessao]) < SCORE_DELTA_MIN:
            return

    nivel = classificar(score)
    tipo = "PRÉ-PULLBACK" if pre_pullback and not pullback_ok else "SETUP"
    exp = expectativa(score, pullback_ok, pre_pullback)

    # 🔔🔊 CONTROLE DE SOM
    if score >= SCORE_SOM_FORTE:
        prefixo_som = "@everyone\n"
    elif score >= SCORE_SOM_MIN:
        prefixo_som = "@here\n"
    else:
        prefixo_som = ""

    # =============================
    # MENSAGEM BASE
    # =============================
    mensagem = (
        f"{prefixo_som}"
        f"📡 {tipo} — {nivel}\n\n"
        f"💱 {symbol}\n"
        f"📈 Direção: {direcao}\n"
        f"🎯 Qualidade: {score}%\n"
        f"`{barra_score(score)}`\n\n"
        f"📈 Tendência H1: {tendencia}\n"
        f"📉 Pullback M15: {'OK' if pullback_ok else 'NÃO'}\n"
        f"📊 ATR: {round(atr, 6)}\n"
        f"🌍 Sessão: {sessao}\n"
        f"🔮 Expectativa: {exp}\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
    )

    # =============================
    # DECISÃO DO MERCADO (NOVA)
    # =============================
    if prob_buy is not None and prob_sell is not None:
        mensagem += (
            f"\n🧠 DECISÃO DO MERCADO\n"
            f"🟢 BUY  → {prob_buy}%\n"
            f"🔴 SELL → {prob_sell}%\n"
        )

    if recomendacao:
        mensagem += f"📌 Recomendação: {recomendacao}\n"

    if modo:
        mensagem += f"⚙️ Modo: {modo}\n"

    mensagem += "\n🧠 Copiloto ativo — decisão consciente"

    enviar_alerta(mensagem, titulo="COPILOTO MT5 🚨")

    # atualiza controles
    ultimo_alerta[chave_sessao] = True
    ultimo_score[chave_sessao] = score

