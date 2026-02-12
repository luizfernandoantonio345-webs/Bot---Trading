import MetaTrader5 as mt5
import config

def calcular_lote(preco_entrada, sl):
    info = mt5.account_info()
    symbol = mt5.symbol_info(config.SYMBOL)

    if info is None or symbol is None:
        return 0.01

    # RISCO POR TRADE (blindado)
    risco_pct = getattr(config, "RISCO_POR_TRADE", 0.25)

    risco_valor = info.balance * (risco_pct / 100)
    stop_dist = abs(preco_entrada - sl)

    if stop_dist <= 0:
        return symbol.volume_min

    valor_por_ponto = symbol.trade_tick_value / symbol.trade_tick_size
    lote = risco_valor / (stop_dist * valor_por_ponto)

    lote = max(symbol.volume_min, min(lote, symbol.volume_max))
    return round(lote, 2)
