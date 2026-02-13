"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI ENGINE #3: MARKET CONTEXT CLASSIFIER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSIBILITY:
Classify current market regime and tradability.
Identify when market is NOT suitable for trading.

CAN VETO IF:
- Market context unsuitable (choppy, low liquidity)
- High-impact news window
- Extreme volatility
- Session not appropriate

CANNOT:
- Force trades in poor conditions
- Ignore market regime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pandas as pd
import numpy as np
from typing import Dict
from dataclasses import dataclass
from enum import Enum


class MarketRegime(str, Enum):
    """Market regime classification"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    CHOPPY = "CHOPPY"
    BREAKOUT = "BREAKOUT"
    CONSOLIDATION = "CONSOLIDATION"


class Tradability(str, Enum):
    """Market tradability classification"""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    UNTRADEABLE = "UNTRADEABLE"


@dataclass
class ContextClassification:
    """Market context classification result"""
    regime: MarketRegime
    tradability: Tradability
    volatility_level: str
    liquidity_level: str
    session: str
    veto: bool
    veto_reason: str
    confidence: float


class MarketContextClassifier:
    """
    Classifies market regime and tradability.
    
    PRINCIPLES:
    - NOT TRADING in poor conditions is valuable
    - Regime identification crucial for strategy selection
    - Volatility and liquidity matter
    - Session timing affects opportunity quality
    """
    
    def __init__(self):
        self.name = "MarketContextClassifier"
        self.version = "1.0.0"
    
    def classify(
        self,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        current_session: str,
        is_news_window: bool
    ) -> ContextClassification:
        """
        Classify market context and tradability.
        
        Returns ContextClassification with veto if untradeable.
        """
        
        # 1. Detect regime
        regime = self._detect_regime(df_h1)
        
        # 2. Assess volatility
        volatility_level = self._assess_volatility(df_m15)
        
        # 3. Assess liquidity
        liquidity_level = self._assess_liquidity(df_m15, current_session)
        
        # 4. Calculate tradability
        tradability = self._calculate_tradability(
            regime,
            volatility_level,
            liquidity_level,
            current_session,
            is_news_window
        )
        
        # 5. Calculate confidence
        confidence = self._calculate_confidence(df_m15, df_h1, regime)
        
        # 6. Veto decision
        veto = False
        veto_reason = ""
        
        if tradability == Tradability.UNTRADEABLE:
            veto = True
            veto_reason = "Market untradeable"
        elif tradability == Tradability.POOR:
            veto = True
            veto_reason = "Market conditions poor"
        elif is_news_window:
            veto = True
            veto_reason = "High-impact news window"
        elif volatility_level == "EXTREME":
            veto = True
            veto_reason = "Extreme volatility detected"
        elif liquidity_level == "VERY_LOW":
            veto = True
            veto_reason = "Liquidity too low"
        
        return ContextClassification(
            regime=regime,
            tradability=tradability,
            volatility_level=volatility_level,
            liquidity_level=liquidity_level,
            session=current_session,
            veto=veto,
            veto_reason=veto_reason,
            confidence=confidence
        )
    
    def _detect_regime(self, df_h1: pd.DataFrame) -> MarketRegime:
        """Detect market regime from H1 data"""
        if len(df_h1) < 50:
            return MarketRegime.RANGING
        
        # Calculate trend using EMAs
        close = df_h1['close']
        ema_20 = close.ewm(span=20).mean()
        ema_50 = close.ewm(span=50).mean()
        
        # Slope analysis
        recent_slope = (close.iloc[-1] - close.iloc[-20]) / 20 if len(close) >= 20 else 0
        
        # Range analysis
        high_20 = df_h1['high'].rolling(20).max()
        low_20 = df_h1['low'].rolling(20).min()
        range_pct = ((high_20.iloc[-1] - low_20.iloc[-1]) / low_20.iloc[-1] * 100) if len(high_20) > 0 else 0
        
        # EMA alignment
        ema_aligned_up = ema_20.iloc[-1] > ema_50.iloc[-1] and recent_slope > 0
        ema_aligned_down = ema_20.iloc[-1] < ema_50.iloc[-1] and recent_slope < 0
        
        # Classification
        if ema_aligned_up and abs(recent_slope) > 0.001:
            return MarketRegime.TRENDING_UP
        elif ema_aligned_down and abs(recent_slope) > 0.001:
            return MarketRegime.TRENDING_DOWN
        elif range_pct < 1.0:  # Tight range
            return MarketRegime.CONSOLIDATION
        elif range_pct < 2.0:
            return MarketRegime.RANGING
        else:
            return MarketRegime.CHOPPY
    
    def _assess_volatility(self, df_m15: pd.DataFrame) -> str:
        """Assess volatility level"""
        if len(df_m15) < 20:
            return "UNKNOWN"
        
        # ATR-based volatility
        high_low = df_m15['high'] - df_m15['low']
        atr = high_low.rolling(14).mean()
        atr_pct = (atr / df_m15['close'] * 100).iloc[-1] if len(atr) > 0 else 0
        
        if atr_pct > 2.0:
            return "EXTREME"
        elif atr_pct > 1.5:
            return "HIGH"
        elif atr_pct > 0.8:
            return "MODERATE"
        elif atr_pct > 0.4:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _assess_liquidity(self, df_m15: pd.DataFrame, session: str) -> str:
        """Assess liquidity level"""
        
        # Session-based liquidity
        session_liquidity = {
            'LONDON': 'HIGH',
            'NY': 'HIGH',
            'LONDON_NY_OVERLAP': 'VERY_HIGH',
            'ASIA': 'MODERATE',
            'OFF_HOURS': 'LOW'
        }
        
        base_liquidity = session_liquidity.get(session, 'MODERATE')
        
        # Adjust based on spread/volatility
        if len(df_m15) >= 10:
            spread_proxy = (df_m15['high'] - df_m15['low']).tail(10).mean()
            if spread_proxy < 0.0005:  # Very tight spread
                return 'VERY_HIGH'
            elif spread_proxy > 0.002:  # Wide spread
                if base_liquidity == 'HIGH':
                    return 'MODERATE'
                elif base_liquidity == 'MODERATE':
                    return 'LOW'
        
        return base_liquidity
    
    def _calculate_tradability(
        self,
        regime: MarketRegime,
        volatility: str,
        liquidity: str,
        session: str,
        is_news: bool
    ) -> Tradability:
        """Calculate overall tradability"""
        
        # News window = untradeable
        if is_news:
            return Tradability.UNTRADEABLE
        
        # Extreme volatility = untradeable
        if volatility == "EXTREME":
            return Tradability.UNTRADEABLE
        
        # Very low liquidity = untradeable
        if liquidity == "VERY_LOW":
            return Tradability.UNTRADEABLE
        
        # Choppy market = poor
        if regime == MarketRegime.CHOPPY:
            return Tradability.POOR
        
        # Off hours = poor unless exceptional conditions
        if session == "OFF_HOURS":
            return Tradability.POOR
        
        # Trending markets with good liquidity = excellent
        if regime in [MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]:
            if liquidity in ['VERY_HIGH', 'HIGH'] and volatility in ['MODERATE', 'HIGH']:
                return Tradability.EXCELLENT
            elif liquidity in ['HIGH', 'MODERATE']:
                return Tradability.GOOD
            else:
                return Tradability.FAIR
        
        # Ranging/consolidation = fair to good
        if regime in [MarketRegime.RANGING, MarketRegime.CONSOLIDATION]:
            if liquidity in ['VERY_HIGH', 'HIGH']:
                return Tradability.GOOD
            else:
                return Tradability.FAIR
        
        return Tradability.FAIR
    
    def _calculate_confidence(
        self,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        regime: MarketRegime
    ) -> float:
        """Calculate confidence in classification"""
        
        # More data = higher confidence
        data_confidence = min(len(df_h1) / 100, 1.0)
        
        # Consistent regime across timeframes = higher confidence
        # (simplified check)
        regime_confidence = 0.8  # Placeholder
        
        return (data_confidence + regime_confidence) / 2
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'active': True
        }
