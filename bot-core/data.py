import MetaTrader5 as mt5
import pandas as pd

def get_data(symbol, timeframe, bars=300):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        return None

    df = pd.DataFrame(rates)

    # 🔥 REMOVE QUALQUER RISCO DE ERRO COM DATETIME
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="s")

    # 🔥 GARANTE COLUNAS NUMÉRICAS
    df = df[[
        "open",
        "high",
        "low",
        "close",
        "tick_volume"
    ]].astype(float)

    return df
