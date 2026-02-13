"""
═══════════════════════════════════════════════════════════════════
MARKET ANALYZER - ANÁLISE MULTICAMADAS PROFISSIONAL
═══════════════════════════════════════════════════════════════════
Analisa estrutura de mercado, tendência, momentum, volatilidade,
volume, liquidez e qualidade de movimento em tempo real.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, time
from enum import Enum


class TrendState(Enum):
    STRONG_UPTREND = "STRONG_UPTREND"
    UPTREND = "UPTREND"
    SIDEWAYS = "SIDEWAYS"
    DOWNTREND = "DOWNTREND"
    STRONG_DOWNTREND = "STRONG_DOWNTREND"


class MarketStructure(Enum):
    HH = "HIGHER_HIGH"      # Higher High
    HL = "HIGHER_LOW"       # Higher Low
    LH = "LOWER_HIGH"       # Lower High
    LL = "LOWER_LOW"        # Lower Low
    NEUTRAL = "NEUTRAL"


class MarketSession(Enum):
    ASIAN = "ASIAN"
    LONDON = "LONDON"
    NEW_YORK = "NEW_YORK"
    OVERLAP = "OVERLAP"
    OFF_HOURS = "OFF_HOURS"


class MarketAnalyzer:
    """
    Analisador de mercado multicamadas para trading profissional.
    Fornece análise completa de estrutura, tendência, momentum e contexto.
    """
    
    def __init__(self):
        self.last_analysis = None
        self.structure_history = []
        
    def analyze_complete_market(
        self,
        df_m5: pd.DataFrame,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        df_h4: pd.DataFrame,
        df_d1: pd.DataFrame,
        current_price: float
    ) -> Dict:
        """
        Análise completa de múltiplos timeframes.
        
        Returns:
            Dict com todas as análises de mercado
        """
        
        analysis = {
            "timestamp": datetime.now(),
            "current_price": current_price,
            
            # Estrutura de mercado
            "structure": self._analyze_market_structure(df_h1),
            
            # Tendências multi-timeframe
            "trend": {
                "d1": self._analyze_trend(df_d1),
                "h4": self._analyze_trend(df_h4),
                "h1": self._analyze_trend(df_h1),
                "m15": self._analyze_trend(df_m15),
                "consensus": None  # Calculado depois
            },
            
            # Momentum
            "momentum": self._analyze_momentum(df_m15, df_h1),
            
            # Volatilidade
            "volatility": self._analyze_volatility(df_m15, df_h1, df_d1),
            
            # Volume e fluxo
            "volume": self._analyze_volume(df_m15, df_h1),
            
            # Liquidez
            "liquidity": self._analyze_liquidity(df_m15),
            
            # Sessão de mercado
            "session": self._get_market_session(),
            
            # Qualidade do movimento atual
            "movement_quality": self._analyze_movement_quality(df_m15),
            
            # Contexto temporal
            "temporal_context": self._analyze_temporal_context()
        }
        
        # Consenso de tendência
        analysis["trend"]["consensus"] = self._calculate_trend_consensus(analysis["trend"])
        
        # Score de qualidade geral do mercado
        analysis["market_health_score"] = self._calculate_market_health(analysis)
        
        self.last_analysis = analysis
        return analysis
    
    def _analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """
        Identifica estrutura de mercado (HH, HL, LH, LL).
        """
        highs = []
        lows = []
        
        # Identifica swing highs e lows
        for i in range(2, len(df) - 2):
            # Swing High
            if (df['high'].iloc[i] > df['high'].iloc[i-1] and 
                df['high'].iloc[i] > df['high'].iloc[i-2] and
                df['high'].iloc[i] > df['high'].iloc[i+1] and 
                df['high'].iloc[i] > df['high'].iloc[i+2]):
                highs.append((i, df['high'].iloc[i]))
            
            # Swing Low
            if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
                df['low'].iloc[i] < df['low'].iloc[i-2] and
                df['low'].iloc[i] < df['low'].iloc[i+1] and 
                df['low'].iloc[i] < df['low'].iloc[i+2]):
                lows.append((i, df['low'].iloc[i]))
        
        structure_type = MarketStructure.NEUTRAL
        
        if len(highs) >= 2 and len(lows) >= 2:
            recent_highs = [h[1] for h in highs[-2:]]
            recent_lows = [l[1] for l in lows[-2:]]
            
            # Higher High + Higher Low = Uptrend
            if recent_highs[-1] > recent_highs[-2] and recent_lows[-1] > recent_lows[-2]:
                structure_type = MarketStructure.HH
            
            # Lower Low + Lower High = Downtrend
            elif recent_highs[-1] < recent_highs[-2] and recent_lows[-1] < recent_lows[-2]:
                structure_type = MarketStructure.LL
            
            # Higher High + Lower Low = Consolidação
            elif recent_highs[-1] > recent_highs[-2] and recent_lows[-1] < recent_lows[-2]:
                structure_type = MarketStructure.NEUTRAL
            
            # Lower High
            elif recent_highs[-1] < recent_highs[-2]:
                structure_type = MarketStructure.LH
            
            # Higher Low
            elif recent_lows[-1] > recent_lows[-2]:
                structure_type = MarketStructure.HL
        
        return {
            "type": structure_type.value,
            "swing_highs": highs[-5:] if len(highs) >= 5 else highs,
            "swing_lows": lows[-5:] if len(lows) >= 5 else lows,
            "strength": self._calculate_structure_strength(highs, lows)
        }
    
    def _calculate_structure_strength(self, highs: List, lows: List) -> float:
        """
        Calcula força da estrutura (0-100).
        """
        if len(highs) < 2 or len(lows) < 2:
            return 0.0
        
        # Consistência dos swings
        high_consistency = 0
        for i in range(1, min(5, len(highs))):
            if highs[-i][1] > highs[-(i+1)][1]:
                high_consistency += 1
        
        low_consistency = 0
        for i in range(1, min(5, len(lows))):
            if lows[-i][1] > lows[-(i+1)][1]:
                low_consistency += 1
        
        strength = ((high_consistency + low_consistency) / 8) * 100
        return round(strength, 2)
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """
        Análise de tendência usando EMAs e ADX.
        """
        if len(df) < 200:
            return {"state": TrendState.SIDEWAYS.value, "strength": 0}
        
        # EMAs
        ema_20 = df['close'].ewm(span=20, adjust=False).mean()
        ema_50 = df['close'].ewm(span=50, adjust=False).mean()
        ema_200 = df['close'].ewm(span=200, adjust=False).mean()
        
        current_price = df['close'].iloc[-1]
        
        # ADX (Average Directional Index)
        adx = self._calculate_adx(df, period=14)
        
        # Determina tendência
        if current_price > ema_20.iloc[-1] > ema_50.iloc[-1] > ema_200.iloc[-1]:
            if adx > 40:
                state = TrendState.STRONG_UPTREND
            else:
                state = TrendState.UPTREND
        elif current_price < ema_20.iloc[-1] < ema_50.iloc[-1] < ema_200.iloc[-1]:
            if adx > 40:
                state = TrendState.STRONG_DOWNTREND
            else:
                state = TrendState.DOWNTREND
        else:
            state = TrendState.SIDEWAYS
        
        # Slope da EMA200 (momentum de longo prazo)
        ema_slope = (ema_200.iloc[-1] - ema_200.iloc[-20]) / ema_200.iloc[-20] * 100
        
        return {
            "state": state.value,
            "strength": float(adx),
            "ema_alignment": self._check_ema_alignment(ema_20, ema_50, ema_200),
            "ema_slope": float(ema_slope),
            "distance_from_ema200": float(abs(current_price - ema_200.iloc[-1]) / ema_200.iloc[-1] * 100)
        }
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        Calcula Average Directional Index.
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0.0
    
    def _check_ema_alignment(self, ema_20, ema_50, ema_200) -> bool:
        """
        Verifica se EMAs estão alinhadas (bullish ou bearish).
        """
        bullish = ema_20.iloc[-1] > ema_50.iloc[-1] > ema_200.iloc[-1]
        bearish = ema_20.iloc[-1] < ema_50.iloc[-1] < ema_200.iloc[-1]
        return bullish or bearish
    
    def _analyze_momentum(self, df_m15: pd.DataFrame, df_h1: pd.DataFrame) -> Dict:
        """
        Análise de momentum real (não apenas indicador).
        """
        # RSI
        rsi_m15 = self._calculate_rsi(df_m15['close'], 14)
        rsi_h1 = self._calculate_rsi(df_h1['close'], 14)
        
        # Rate of Change
        roc_m15 = ((df_m15['close'].iloc[-1] - df_m15['close'].iloc[-10]) / 
                   df_m15['close'].iloc[-10] * 100)
        
        # Momentum Score
        momentum_score = 50  # Base
        
        if 40 < rsi_m15 < 60:
            momentum_score += 10  # Zona neutra favorável
        elif rsi_m15 > 70 or rsi_m15 < 30:
            momentum_score -= 20  # Extremos perigosos
        
        if abs(roc_m15) > 0.5:
            momentum_score += 15  # Movimento forte
        
        # Convergência de timeframes
        if (rsi_m15 > 50 and rsi_h1 > 50) or (rsi_m15 < 50 and rsi_h1 < 50):
            momentum_score += 15  # Alinhamento
        
        return {
            "rsi_m15": float(rsi_m15),
            "rsi_h1": float(rsi_h1),
            "rate_of_change": float(roc_m15),
            "score": max(0, min(100, momentum_score)),
            "direction": "BULLISH" if rsi_m15 > 50 else "BEARISH",
            "strength": "STRONG" if abs(rsi_m15 - 50) > 20 else "MODERATE"
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """
        Calcula Relative Strength Index.
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _analyze_volatility(
        self, 
        df_m15: pd.DataFrame, 
        df_h1: pd.DataFrame,
        df_d1: pd.DataFrame
    ) -> Dict:
        """
        Análise de volatilidade atual vs histórica.
        """
        # ATR multi-timeframe
        atr_m15 = self._calculate_atr(df_m15, 14)
        atr_h1 = self._calculate_atr(df_h1, 14)
        atr_d1 = self._calculate_atr(df_d1, 14)
        
        # Volatilidade histórica (desvio padrão)
        hist_vol_m15 = df_m15['close'].pct_change().rolling(window=20).std() * 100
        
        # Bollinger Bands width
        bb_width = self._calculate_bb_width(df_m15, 20, 2)
        
        # Volatilidade atual vs média
        current_vol = hist_vol_m15.iloc[-1]
        avg_vol = hist_vol_m15.mean()
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
        
        # Classificação
        if vol_ratio > 1.5:
            classification = "MUITO_ALTA"
        elif vol_ratio > 1.2:
            classification = "ALTA"
        elif vol_ratio > 0.8:
            classification = "NORMAL"
        else:
            classification = "BAIXA"
        
        return {
            "atr_m15": float(atr_m15),
            "atr_h1": float(atr_h1),
            "atr_d1": float(atr_d1),
            "current_volatility": float(current_vol),
            "average_volatility": float(avg_vol),
            "volatility_ratio": float(vol_ratio),
            "classification": classification,
            "bb_width": float(bb_width),
            "is_expanding": float(bb_width) > float(df_m15['close'].rolling(20).std().iloc[-20] * 4)
        }
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        Calcula Average True Range.
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0
    
    def _calculate_bb_width(self, df: pd.DataFrame, period: int = 20, std: float = 2) -> float:
        """
        Calcula largura das Bollinger Bands.
        """
        sma = df['close'].rolling(window=period).mean()
        std_dev = df['close'].rolling(window=period).std()
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        width = ((upper - lower) / sma) * 100
        return float(width.iloc[-1]) if not pd.isna(width.iloc[-1]) else 0.0
    
    def _analyze_volume(self, df_m15: pd.DataFrame, df_h1: pd.DataFrame) -> Dict:
        """
        Análise de volume e fluxo.
        """
        if 'volume' not in df_m15.columns or 'volume' not in df_h1.columns:
            return {
                "available": False,
                "message": "Volume data not available"
            }
        
        # Volume médio
        avg_vol_m15 = df_m15['volume'].rolling(window=20).mean()
        current_vol = df_m15['volume'].iloc[-1]
        
        # Ratio atual vs média
        vol_ratio = current_vol / avg_vol_m15.iloc[-1] if avg_vol_m15.iloc[-1] > 0 else 1.0
        
        # Volume em tendência
        price_change = df_m15['close'].iloc[-1] - df_m15['close'].iloc[-5]
        vol_trend_alignment = (price_change > 0 and vol_ratio > 1.2) or (price_change < 0 and vol_ratio > 1.2)
        
        return {
            "available": True,
            "current_volume": float(current_vol),
            "average_volume": float(avg_vol_m15.iloc[-1]),
            "volume_ratio": float(vol_ratio),
            "classification": "HIGH" if vol_ratio > 1.5 else "NORMAL" if vol_ratio > 0.8 else "LOW",
            "trend_confirmation": vol_trend_alignment
        }
    
    def _analyze_liquidity(self, df: pd.DataFrame) -> Dict:
        """
        Análise de liquidez com base em spread e range.
        """
        # Spread estimado (high - low do último candle)
        last_candle_range = df['high'].iloc[-1] - df['low'].iloc[-1]
        avg_range = (df['high'] - df['low']).rolling(window=20).mean().iloc[-1]
        
        # Range ratio
        range_ratio = last_candle_range / avg_range if avg_range > 0 else 1.0
        
        # Gaps (diferença entre close e próximo open)
        if len(df) > 1:
            gap = abs(df['open'].iloc[-1] - df['close'].iloc[-2])
            gap_size = gap / df['close'].iloc[-2] * 100
        else:
            gap_size = 0.0
        
        # Score de liquidez
        liquidity_score = 100
        
        if range_ratio > 2.0:
            liquidity_score -= 30  # Range muito alto = baixa liquidez
        
        if gap_size > 0.1:
            liquidity_score -= 20  # Gap grande = problema de liquidez
        
        return {
            "last_candle_range": float(last_candle_range),
            "average_range": float(avg_range),
            "range_ratio": float(range_ratio),
            "gap_size_percent": float(gap_size),
            "score": max(0, liquidity_score),
            "classification": "GOOD" if liquidity_score > 70 else "MODERATE" if liquidity_score > 50 else "POOR"
        }
    
    def _get_market_session(self) -> Dict:
        """
        Identifica sessão de mercado atual (UTC).
        """
        now = datetime.utcnow()
        hour = now.hour
        
        # Asian: 00:00 - 09:00 UTC
        # London: 07:00 - 16:00 UTC
        # New York: 12:00 - 21:00 UTC
        
        if 0 <= hour < 7:
            session = MarketSession.ASIAN
            quality = 40  # Menor volatilidade
        elif 7 <= hour < 12:
            session = MarketSession.LONDON
            quality = 85  # Alta volatilidade
        elif 12 <= hour < 16:
            session = MarketSession.OVERLAP
            quality = 95  # Máxima volatilidade
        elif 16 <= hour < 21:
            session = MarketSession.NEW_YORK
            quality = 80  # Alta volatilidade
        else:
            session = MarketSession.OFF_HOURS
            quality = 30  # Baixa atividade
        
        return {
            "current": session.value,
            "hour_utc": hour,
            "quality_score": quality,
            "is_favorable": quality >= 70
        }
    
    def _analyze_movement_quality(self, df: pd.DataFrame) -> Dict:
        """
        Avalia qualidade do movimento atual.
        """
        last_candles = df.tail(5)
        
        # Body vs wick ratio (últimos 5 candles)
        body_ratios = []
        for _, candle in last_candles.iterrows():
            body = abs(candle['close'] - candle['open'])
            total_range = candle['high'] - candle['low']
            ratio = body / total_range if total_range > 0 else 0
            body_ratios.append(ratio)
        
        avg_body_ratio = sum(body_ratios) / len(body_ratios)
        
        # Sequência de candles
        bullish_count = sum(1 for _, c in last_candles.iterrows() if c['close'] > c['open'])
        bearish_count = 5 - bullish_count
        
        # Score de qualidade
        quality_score = 50
        
        if avg_body_ratio > 0.6:
            quality_score += 25  # Candles fortes
        elif avg_body_ratio < 0.3:
            quality_score -= 15  # Candles fracos
        
        if bullish_count >= 4 or bearish_count >= 4:
            quality_score += 15  # Movimento consistente
        
        return {
            "average_body_ratio": float(avg_body_ratio),
            "bullish_candles": bullish_count,
            "bearish_candles": bearish_count,
            "quality_score": max(0, min(100, quality_score)),
            "classification": "STRONG" if quality_score > 70 else "MODERATE" if quality_score > 50 else "WEAK"
        }
    
    def _analyze_temporal_context(self) -> Dict:
        """
        Contexto temporal (dia da semana, início/fim de mês, etc).
        """
        now = datetime.now()
        
        # Dia da semana (0=Monday, 6=Sunday)
        weekday = now.weekday()
        
        # Favorabilidade por dia
        day_quality = {
            0: 75,  # Monday - volatile
            1: 85,  # Tuesday - good
            2: 90,  # Wednesday - best
            3: 85,  # Thursday - good
            4: 70,  # Friday - choppy
            5: 30,  # Saturday - low
            6: 30   # Sunday - low
        }
        
        # Início/fim de mês
        is_month_start = now.day <= 5
        is_month_end = now.day >= 25
        
        return {
            "weekday": weekday,
            "day_name": now.strftime("%A"),
            "day_quality": day_quality[weekday],
            "is_month_start": is_month_start,
            "is_month_end": is_month_end,
            "is_weekend": weekday >= 5
        }
    
    def _calculate_trend_consensus(self, trends: Dict) -> Dict:
        """
        Calcula consenso de tendência entre timeframes.
        """
        weights = {
            "d1": 0.35,
            "h4": 0.30,
            "h1": 0.20,
            "m15": 0.15
        }
        
        bullish_score = 0
        bearish_score = 0
        
        for tf, weight in weights.items():
            state = trends[tf]["state"]
            if "UPTREND" in state:
                bullish_score += weight * 100
            elif "DOWNTREND" in state:
                bearish_score += weight * 100
        
        if bullish_score > bearish_score + 30:
            consensus = "BULLISH"
            strength = bullish_score
        elif bearish_score > bullish_score + 30:
            consensus = "BEARISH"
            strength = bearish_score
        else:
            consensus = "NEUTRAL"
            strength = 50
        
        return {
            "direction": consensus,
            "strength": round(strength, 2),
            "bullish_score": round(bullish_score, 2),
            "bearish_score": round(bearish_score, 2)
        }
    
    def _calculate_market_health(self, analysis: Dict) -> int:
        """
        Score de saúde geral do mercado (0-100).
        """
        score = 0
        
        # Estrutura (20 pontos)
        score += analysis["structure"]["strength"] * 0.20
        
        # Tendência (25 pontos)
        trend_strength = analysis["trend"]["consensus"]["strength"]
        score += trend_strength * 0.25
        
        # Momentum (20 pontos)
        score += analysis["momentum"]["score"] * 0.20
        
        # Volatilidade (15 pontos)
        vol_ratio = analysis["volatility"]["volatility_ratio"]
        if 0.8 <= vol_ratio <= 1.5:
            score += 15  # Volatilidade ideal
        elif vol_ratio < 0.8:
            score += 8   # Baixa
        else:
            score += 5   # Muito alta
        
        # Liquidez (10 pontos)
        score += analysis["liquidity"]["score"] * 0.10
        
        # Sessão (10 pontos)
        score += analysis["session"]["quality_score"] * 0.10
        
        return max(0, min(100, int(score)))


if __name__ == "__main__":
    print("Market Analyzer - Sistema de Análise Multicamadas")
    print("Módulo pronto para integração")
