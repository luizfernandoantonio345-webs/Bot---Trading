import MetaTrader5 as mt5
from config import SYMBOL, MAGIC
import risk_manager
from copilot_adapter import send_to_copilot


# =============================
# EXECUTAR ORDEM (BUY / SELL)
# =============================
def executar_ordem(direcao, sl, tp, confidence=0):
    # 🔒 Segurança extra
    if risk_manager.posicao_ativa():
        print("⚠️ Já existe posição ativa — ordem cancelada")
        return False

    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print("❌ Símbolo não encontrado:", SYMBOL)
        return False

    if not symbol_info.visible:
        mt5.symbol_select(SYMBOL, True)

    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        print("❌ Erro ao obter tick do símbolo")
        return False

    price = tick.ask if direcao == "BUY" else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": calcular_lote(),
        "type": mt5.ORDER_TYPE_BUY if direcao == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": MAGIC,
        "comment": "BOT_MT5_v2",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result is None:
        print("❌ Erro: order_send retornou None")
        return False

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Ordem rejeitada | retcode={result.retcode}")
        return False

    # =============================
    # ✅ ORDEM EXECUTADA
    # =============================
    print(f"✅ ORDEM EXECUTADA: {direcao} | Ticket: {result.order}")

    # 🔌 ENVIA PARA O TRADING COPILOT
    send_to_copilot(
        pair=SYMBOL,
        side=direcao,
        confidence=confidence,
        result="OPEN"
    )

    return True


# =============================
# LOTE (CENTRALIZADO)
# =============================
def calcular_lote():
    """
    Mantém simples por enquanto.
    Pode evoluir depois para risco percentual.
    """
    return 0.01
