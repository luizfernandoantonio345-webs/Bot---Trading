import pandas as pd

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def atr(df, period=14):
    df = df[["high", "low", "close"]].copy()

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()
