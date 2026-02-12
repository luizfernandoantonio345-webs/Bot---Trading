import MetaTrader5 as mt5
from datetime import datetime, date
from config import MAGIC, SYMBOL
from risk_config import get_risk_config
from strategy import atualizar_resultado
from copilot_adapter import send_to_copilot  # 🔌 integração Copilot

risk = get_risk_config()

MAX_DAILY_RISK = risk["MAX_DAILY_RISK"]
DAILY_PROFIT_TARGET = risk["DAILY_PROFIT_TARGET"]
MAX_TRADES_PER_DAY = risk["MAX_TRADES_PER_DAY"]
MAX_CONSECUTIVE_LOSSES = risk["MAX_CONSECUTIVE_LOSSES"]
REAL_SAFE = risk["REAL_SAFE"]

daily_loss = 0.0
daily_profit = 0.0
trades_today = 0
consecutive_losses = 0
paused = False
last_day = date.today()
last_ticket = 0


# =============================
# RESET DIÁRIO
# =============================
def reset_daily_limits():
    global daily_loss, daily_profit, trades_today, consecutive_losses, paused, last_day
    today = date.today()
    if today != last_day:
        daily_loss = 0
        daily_profit = 0
        trades_today = 0
        consecutive_losses = 0
        paused = False
        last_day = today


# =============================
# POSIÇÃO ATIVA
# =============================
def posicao_ativa():
    positions = mt5.positions_get(symbol=SYMBOL)
    return positions is not None and len(positions) > 0


# =============================
# PODE OPERAR?
# =============================
def can_trade():
    reset_daily_limits()

    if paused:
        return False
    if posicao_ativa():
        return False
    if trades_today >= MAX_TRADES_PER_DAY:
        return False
    if daily_loss >= MAX_DAILY_RISK:
        return False
    if daily_profit >= DAILY_PROFIT_TARGET:
        return False
    if consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
        return False
    return True


# =============================
# FECHAMENTO DE TRADES
# =============================
def check_closed_trades():
    global daily_loss, daily_profit, trades_today, consecutive_losses, paused, last_ticket

    deals = mt5.history_deals_get(
        datetime.combine(date.today(), datetime.min.time()),
        datetime.now()
    )

    if deals is None:
        return

    for d in deals:
        if d.magic != MAGIC:
            continue
        if d.ticket <= last_ticket:
            continue
        if d.entry != mt5.DEAL_ENTRY_OUT:
            continue

        last_ticket = d.ticket
        trades_today += 1

        direcao = "BUY" if d.type == mt5.ORDER_TYPE_BUY else "SELL"
        ganhou = d.profit > 0

        # 🔁 mantém sua lógica interna
        atualizar_resultado(direcao, ganhou)

        # 🔥 RESULTADO PARA O COPILOT
        send_to_copilot(
            pair=SYMBOL,
            side=direcao,
            confidence=0,  # já foi calculada na entrada
            result="WIN" if ganhou else "LOSS"
        )

        if ganhou:
            daily_profit += d.profit
            consecutive_losses = 0
        else:
            daily_loss += abs(d.profit)
            consecutive_losses += 1

        if REAL_SAFE:
            if daily_loss >= MAX_DAILY_RISK:
                paused = True
            if daily_profit >= DAILY_PROFIT_TARGET:
                paused = True
            if consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
                paused = True
