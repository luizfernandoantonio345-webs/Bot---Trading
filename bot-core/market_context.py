"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MARKET CONTEXT ANALYZER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Intelligent market regime detection for visual context.
Classifies market conditions to help users understand
WHY certain decisions are made or blocked.

OUTPUT: Subtle chart background shading, not aggressive alerts.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
from events import MarketContext, RiskLevel
from indicators import atr, ema


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MARKET REGIME CLASSIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_market_context(df_m15: pd.DataFrame, df_h1: pd.DataFrame) -> dict:
    """
    Comprehensive market analysis for intelligent decision context.
    
    Returns:
        {
            "context": MarketContext enum,
            "risk_level": RiskLevel enum,
            "volatility": float,
            "liquidity_score": float,
            "session": str,
            "trend_strength": float,
            "is_tradeable": bool,
            "reason": str
        }
    """
    
    # Get current market data
    current_price = float(df_m15["close"].iloc[-1])
    atr_val = float(atr(df_m15, 14).iloc[-1])
    
    # Calculate EMAs
    ema_20 = float(ema(df_m15["close"], 20).iloc[-1])
    ema_50 = float(ema(df_m15["close"], 50).iloc[-1])
    ema_200_h1 = float(ema(df_h1["close"], 200).iloc[-1])
    
    # ━━━━━ TREND DETECTION ━━━━━
    trend_strength = calculate_trend_strength(df_h1)
    
    # ━━━━━ VOLATILITY ASSESSMENT ━━━━━
    volatility_score = calculate_volatility(df_m15, atr_val)
    
    # ━━━━━ LIQUIDITY ASSESSMENT ━━━━━
    liquidity_score = calculate_liquidity(df_m15)
    
    # ━━━━━ SESSION DETECTION ━━━━━
    session = get_trading_session()
    
    # ━━━━━ NEWS WINDOW CHECK ━━━━━
    is_news_window = check_news_window()
    
    # ━━━━━ CONTEXT CLASSIFICATION ━━━━━
    context, reason = classify_context(
        trend_strength=trend_strength,
        volatility_score=volatility_score,
        liquidity_score=liquidity_score,
        session=session,
        is_news_window=is_news_window
    )
    
    # ━━━━━ RISK LEVEL ━━━━━
    risk_level = calculate_risk_level(
        volatility_score=volatility_score,
        liquidity_score=liquidity_score,
        session=session,
        is_news_window=is_news_window
    )
    
    # ━━━━━ TRADEABILITY ━━━━━
    is_tradeable = assess_tradeability(
        context=context,
        risk_level=risk_level,
        session=session
    )
    
    return {
        "context": context,
        "risk_level": risk_level,
        "volatility": volatility_score,
        "liquidity_score": liquidity_score,
        "session": session,
        "trend_strength": trend_strength,
        "is_tradeable": is_tradeable,
        "reason": reason,
        "atr": atr_val,
        "current_price": current_price
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TREND STRENGTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_trend_strength(df: pd.DataFrame) -> float:
    """
    Calculate trend strength (0-1).
    Uses ADX-like logic without complexity.
    """
    if len(df) < 20:
        return 0.0
    
    close = df["close"].values
    
    # Price momentum
    momentum = (close[-1] - close[-20]) / close[-20]
    
    # EMA alignment
    ema_20 = ema(df["close"], 20).iloc[-1]
    ema_50 = ema(df["close"], 50).iloc[-1]
    ema_alignment = abs(ema_20 - ema_50) / ema_50
    
    # Combine
    strength = min(1.0, abs(momentum) * 5 + ema_alignment * 2)
    
    return round(strength, 2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VOLATILITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_volatility(df: pd.DataFrame, atr_val: float) -> float:
    """
    Volatility score (0-1).
    0 = dead market, 1 = extreme volatility
    """
    if len(df) < 50:
        return 0.5
    
    # ATR relative to price
    price = float(df["close"].iloc[-1])
    atr_pct = (atr_val / price) * 100
    
    # Recent range expansion
    recent_range = df["high"].iloc[-10:].max() - df["low"].iloc[-10:].min()
    avg_range = df["high"].iloc[-50:-10].max() - df["low"].iloc[-50:-10].min()
    
    range_expansion = recent_range / max(avg_range, 0.00001)
    
    # Volatility score
    vol_score = min(1.0, (atr_pct / 0.5) * 0.5 + (range_expansion - 1) * 0.5)
    
    return max(0.0, min(1.0, vol_score))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIQUIDITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_liquidity(df: pd.DataFrame) -> float:
    """
    Liquidity proxy score (0-1).
    Based on candle bodies vs wicks ratio.
    """
    if len(df) < 10:
        return 0.5
    
    recent = df.iloc[-10:]
    
    # Body vs total range
    bodies = abs(recent["close"] - recent["open"])
    ranges = recent["high"] - recent["low"]
    
    body_ratio = (bodies / ranges.replace(0, 0.00001)).mean()
    
    return min(1.0, max(0.0, body_ratio))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRADING SESSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_trading_session() -> str:
    """Get current trading session"""
    now = datetime.now()
    hour = now.hour
    
    if 0 <= hour < 7:
        return "ASIA"
    elif 7 <= hour < 12:
        return "LONDON"
    elif 12 <= hour < 17:
        return "NY"
    elif 17 <= hour < 20:
        return "OVERLAP"
    else:
        return "OFF"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEWS WINDOW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_news_window() -> bool:
    """
    Check if we're in high-impact news window.
    This is a simplified version - integrate with economic calendar API.
    """
    now = datetime.now()
    
    # Major news times (EST)
    # 8:30 AM = NFP, CPI, etc.
    # 2:00 PM = FOMC
    
    news_hours = [8, 14]
    news_window_minutes = 30
    
    for news_hour in news_hours:
        news_time = time(news_hour, 30)
        current_time = now.time()
        
        # Check if within +/- 30 min of news time
        time_diff = abs(
            (current_time.hour * 60 + current_time.minute) - 
            (news_time.hour * 60 + news_time.minute)
        )
        
        if time_diff <= news_window_minutes:
            return True
    
    return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTEXT CLASSIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def classify_context(
    trend_strength: float,
    volatility_score: float,
    liquidity_score: float,
    session: str,
    is_news_window: bool
) -> tuple[MarketContext, str]:
    """
    Classify market context with human-readable reason.
    
    Returns:
        (MarketContext, reason_string)
    """
    
    # NEWS WINDOW — highest priority
    if is_news_window:
        return (
            MarketContext.NEWS_WINDOW,
            "High-impact news event expected — increased uncertainty"
        )
    
    # VOLATILE
    if volatility_score > 0.75:
        return (
            MarketContext.VOLATILE,
            "Extreme price swings detected — exercise caution"
        )
    
    # LOW LIQUIDITY
    if liquidity_score < 0.3 or session in ["ASIA", "OFF"]:
        return (
            MarketContext.LOW_LIQUIDITY,
            "Low market participation — spreads may widen"
        )
    
    # TRENDING
    if trend_strength > 0.6:
        return (
            MarketContext.TRENDING,
            "Clear directional movement — momentum-based setups"
        )
    
    # RANGING
    if trend_strength < 0.3 and volatility_score < 0.4:
        return (
            MarketContext.RANGING,
            "Sideways price action — support/resistance focus"
        )
    
    # DEFAULT
    return (
        MarketContext.UNKNOWN,
        "Market context unclear — waiting for better structure"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RISK LEVEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_risk_level(
    volatility_score: float,
    liquidity_score: float,
    session: str,
    is_news_window: bool
) -> RiskLevel:
    """Calculate overall risk level"""
    
    if is_news_window:
        return RiskLevel.EXTREME
    
    if volatility_score > 0.8 or liquidity_score < 0.2:
        return RiskLevel.HIGH
    
    if volatility_score > 0.5 or liquidity_score < 0.4 or session == "OFF":
        return RiskLevel.MODERATE
    
    return RiskLevel.LOW


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRADEABILITY ASSESSMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def assess_tradeability(
    context: MarketContext,
    risk_level: RiskLevel,
    session: str
) -> bool:
    """
    Determine if market conditions are suitable for trading.
    This is advisory only — final decision is strategy + risk manager.
    """
    
    # Block news windows
    if context == MarketContext.NEWS_WINDOW:
        return False
    
    # Block extreme risk
    if risk_level == RiskLevel.EXTREME:
        return False
    
    # Block off-hours low liquidity
    if context == MarketContext.LOW_LIQUIDITY and session == "OFF":
        return False
    
    # Allow trending and ranging in good sessions
    if context in [MarketContext.TRENDING, MarketContext.RANGING]:
        if session in ["LONDON", "NY", "OVERLAP"]:
            return True
    
    # Volatile markets require high confidence
    if context == MarketContext.VOLATILE:
        return True  # Allow but increase confidence threshold in strategy
    
    return False
