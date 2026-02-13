"""
═══════════════════════════════════════════════════════════════════
PATTERN ENGINE - DETECÇÃO E CLASSIFICAÇÃO DE PADRÕES
═══════════════════════════════════════════════════════════════════
Identifica padrões técnicos, formações de candles, suporte/resistência
e valida qualidade de sinais para trading profissional.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CandlePattern(Enum):
    ENGULFING_BULLISH = "ENGULFING_BULLISH"
    ENGULFING_BEARISH = "ENGULFING_BEARISH"
    HAMMER = "HAMMER"
    SHOOTING_STAR = "SHOOTING_STAR"
    DOJI = "DOJI"
    MORNING_STAR = "MORNING_STAR"
    EVENING_STAR = "EVENING_STAR"
    THREE_WHITE_SOLDIERS = "THREE_WHITE_SOLDIERS"
    THREE_BLACK_CROWS = "THREE_BLACK_CROWS"
    PIN_BAR_BULLISH = "PIN_BAR_BULLISH"
    PIN_BAR_BEARISH = "PIN_BAR_BEARISH"
    NONE = "NONE"


class ChartPattern(Enum):
    TRIANGLE_ASCENDING = "TRIANGLE_ASCENDING"
    TRIANGLE_DESCENDING = "TRIANGLE_DESCENDING"
    TRIANGLE_SYMMETRICAL = "TRIANGLE_SYMMETRICAL"
    DOUBLE_TOP = "DOUBLE_TOP"
    DOUBLE_BOTTOM = "DOUBLE_BOTTOM"
    HEAD_SHOULDERS = "HEAD_SHOULDERS"
    INVERSE_HEAD_SHOULDERS = "INVERSE_HEAD_SHOULDERS"
    FLAG_BULLISH = "FLAG_BULLISH"
    FLAG_BEARISH = "FLAG_BEARISH"
    CHANNEL_UP = "CHANNEL_UP"
    CHANNEL_DOWN = "CHANNEL_DOWN"
    NONE = "NONE"


@dataclass
class PatternSignal:
    pattern_type: str
    direction: str  # BULLISH, BEARISH, NEUTRAL
    strength: float  # 0-100
    confidence: float  # 0-100
    price_target: Optional[float]
    stop_loss: Optional[float]
    timeframe: str
    detected_at: pd.Timestamp
    context: Dict


class PatternEngine:
    """
    Motor de detecção e validação de padrões técnicos.
    Identifica padrões de candles e formações de preço com validação rigorosa.
    """
    
    def __init__(self):
        self.detected_patterns = []
        self.pattern_history = []
        
    def detect_all_patterns(
        self,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        df_h4: pd.DataFrame,
        support_resistance: Dict
    ) -> Dict:
        """
        Detecção completa de padrões em múltiplos timeframes.
        
        Returns:
            Dict com todos os padrões detectados e análise
        """
        
        patterns = {
            "candle_patterns": {
                "m15": self._detect_candle_patterns(df_m15),
                "h1": self._detect_candle_patterns(df_h1),
                "h4": self._detect_candle_patterns(df_h4)
            },
            
            "chart_patterns": {
                "h1": self._detect_chart_patterns(df_h1),
                "h4": self._detect_chart_patterns(df_h4)
            },
            
            "support_resistance": support_resistance,
            
            "price_action": {
                "m15": self._analyze_price_action(df_m15),
                "h1": self._analyze_price_action(df_h1)
            },
            
            "breakout_signals": self._detect_breakouts(df_h1, support_resistance),
            
            "reversal_signals": self._detect_reversals(df_m15, df_h1),
            
            "continuation_signals": self._detect_continuations(df_m15, df_h1)
        }
        
        # Score agregado de qualidade dos padrões
        patterns["aggregate_score"] = self._calculate_pattern_quality(patterns)
        
        # Sinal principal (se houver)
        patterns["primary_signal"] = self._determine_primary_signal(patterns)
        
        return patterns
    
    def _detect_candle_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detecta padrões de candles (última barra e combinações).
        """
        if len(df) < 5:
            return []
        
        patterns = []
        
        # Engulfing Bullish
        if self._is_engulfing_bullish(df):
            patterns.append({
                "type": CandlePattern.ENGULFING_BULLISH.value,
                "direction": "BULLISH",
                "strength": self._calculate_candle_pattern_strength(df, "ENGULFING"),
                "confidence": 75
            })
        
        # Engulfing Bearish
        if self._is_engulfing_bearish(df):
            patterns.append({
                "type": CandlePattern.ENGULFING_BEARISH.value,
                "direction": "BEARISH",
                "strength": self._calculate_candle_pattern_strength(df, "ENGULFING"),
                "confidence": 75
            })
        
        # Hammer (bullish reversal)
        if self._is_hammer(df):
            patterns.append({
                "type": CandlePattern.HAMMER.value,
                "direction": "BULLISH",
                "strength": 65,
                "confidence": 60
            })
        
        # Shooting Star (bearish reversal)
        if self._is_shooting_star(df):
            patterns.append({
                "type": CandlePattern.SHOOTING_STAR.value,
                "direction": "BEARISH",
                "strength": 65,
                "confidence": 60
            })
        
        # Doji (indecisão)
        if self._is_doji(df):
            patterns.append({
                "type": CandlePattern.DOJI.value,
                "direction": "NEUTRAL",
                "strength": 50,
                "confidence": 70
            })
        
        # Pin Bar Bullish
        if self._is_pin_bar_bullish(df):
            patterns.append({
                "type": CandlePattern.PIN_BAR_BULLISH.value,
                "direction": "BULLISH",
                "strength": 70,
                "confidence": 65
            })
        
        # Pin Bar Bearish
        if self._is_pin_bar_bearish(df):
            patterns.append({
                "type": CandlePattern.PIN_BAR_BEARISH.value,
                "direction": "BEARISH",
                "strength": 70,
                "confidence": 65
            })
        
        # Three White Soldiers
        if self._is_three_white_soldiers(df):
            patterns.append({
                "type": CandlePattern.THREE_WHITE_SOLDIERS.value,
                "direction": "BULLISH",
                "strength": 85,
                "confidence": 80
            })
        
        # Three Black Crows
        if self._is_three_black_crows(df):
            patterns.append({
                "type": CandlePattern.THREE_BLACK_CROWS.value,
                "direction": "BEARISH",
                "strength": 85,
                "confidence": 80
            })
        
        return patterns
    
    def _is_engulfing_bullish(self, df: pd.DataFrame) -> bool:
        """Verifica padrão Engulfing Bullish."""
        if len(df) < 2:
            return False
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        # Candle anterior bearish, atual bullish e envolve o anterior
        prev_bearish = prev['close'] < prev['open']
        curr_bullish = curr['close'] > curr['open']
        engulfing = curr['open'] < prev['close'] and curr['close'] > prev['open']
        
        return prev_bearish and curr_bullish and engulfing
    
    def _is_engulfing_bearish(self, df: pd.DataFrame) -> bool:
        """Verifica padrão Engulfing Bearish."""
        if len(df) < 2:
            return False
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        # Candle anterior bullish, atual bearish e envolve o anterior
        prev_bullish = prev['close'] > prev['open']
        curr_bearish = curr['close'] < curr['open']
        engulfing = curr['open'] > prev['close'] and curr['close'] < prev['open']
        
        return prev_bullish and curr_bearish and engulfing
    
    def _is_hammer(self, df: pd.DataFrame) -> bool:
        """Verifica padrão Hammer."""
        if len(df) < 1:
            return False
        
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        # Lower shadow > 2x body e upper shadow pequena
        return (lower_shadow > body * 2 and 
                upper_shadow < body * 0.5 and
                body > 0)
    
    def _is_shooting_star(self, df: pd.DataFrame) -> bool:
        """Verifica padrão Shooting Star."""
        if len(df) < 1:
            return False
        
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        # Upper shadow > 2x body e lower shadow pequena
        return (upper_shadow > body * 2 and 
                lower_shadow < body * 0.5 and
                body > 0)
    
    def _is_doji(self, df: pd.DataFrame) -> bool:
        """Verifica padrão Doji."""
        if len(df) < 1:
            return False
        
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        # Body muito pequeno (<5% do range total)
        return total_range > 0 and (body / total_range) < 0.05
    
    def _is_pin_bar_bullish(self, df: pd.DataFrame) -> bool:
        """Verifica Pin Bar Bullish."""
        if len(df) < 1:
            return False
        
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        # Lower wick > 60% do range total
        return (total_range > 0 and 
                lower_shadow / total_range > 0.6 and
                candle['close'] > candle['open'])
    
    def _is_pin_bar_bearish(self, df: pd.DataFrame) -> bool:
        """Verifica Pin Bar Bearish."""
        if len(df) < 1:
            return False
        
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        # Upper wick > 60% do range total
        return (total_range > 0 and 
                upper_shadow / total_range > 0.6 and
                candle['close'] < candle['open'])
    
    def _is_three_white_soldiers(self, df: pd.DataFrame) -> bool:
        """Verifica padrão Three White Soldiers."""
        if len(df) < 3:
            return False
        
        last_three = df.tail(3)
        
        # Três candles bullish consecutivos
        all_bullish = all(row['close'] > row['open'] for _, row in last_three.iterrows())
        
        if not all_bullish:
            return False
        
        # Cada close maior que o anterior
        closes = last_three['close'].values
        sequential_higher = all(closes[i] > closes[i-1] for i in range(1, len(closes)))
        
        # Bodies similares (não muito pequenos)
        bodies = [abs(row['close'] - row['open']) for _, row in last_three.iterrows()]
        avg_body = sum(bodies) / len(bodies)
        consistent_bodies = all(b > avg_body * 0.7 for b in bodies)
        
        return sequential_higher and consistent_bodies
    
    def _is_three_black_crows(self, df: pd.DataFrame) -> bool:
        """Verifica padrão Three Black Crows."""
        if len(df) < 3:
            return False
        
        last_three = df.tail(3)
        
        # Três candles bearish consecutivos
        all_bearish = all(row['close'] < row['open'] for _, row in last_three.iterrows())
        
        if not all_bearish:
            return False
        
        # Cada close menor que o anterior
        closes = last_three['close'].values
        sequential_lower = all(closes[i] < closes[i-1] for i in range(1, len(closes)))
        
        # Bodies similares (não muito pequenos)
        bodies = [abs(row['close'] - row['open']) for _, row in last_three.iterrows()]
        avg_body = sum(bodies) / len(bodies)
        consistent_bodies = all(b > avg_body * 0.7 for b in bodies)
        
        return sequential_lower and consistent_bodies
    
    def _calculate_candle_pattern_strength(self, df: pd.DataFrame, pattern_type: str) -> float:
        """
        Calcula força do padrão de candle com base em contexto.
        """
        strength = 50.0
        
        candle = df.iloc[-1]
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        # Body ratio
        if total_range > 0:
            body_ratio = body / total_range
            strength += body_ratio * 30
        
        # Volume (se disponível)
        if 'volume' in df.columns:
            avg_vol = df['volume'].tail(20).mean()
            curr_vol = candle['volume']
            if curr_vol > avg_vol * 1.5:
                strength += 20
        
        return min(100, max(0, strength))
    
    def _detect_chart_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detecta padrões de gráfico (formações de preço).
        """
        patterns = []
        
        if len(df) < 50:
            return patterns
        
        # Double Top
        double_top = self._detect_double_top(df)
        if double_top:
            patterns.append(double_top)
        
        # Double Bottom
        double_bottom = self._detect_double_bottom(df)
        if double_bottom:
            patterns.append(double_bottom)
        
        # Triangles
        triangle = self._detect_triangle(df)
        if triangle:
            patterns.append(triangle)
        
        # Channels
        channel = self._detect_channel(df)
        if channel:
            patterns.append(channel)
        
        return patterns
    
    def _detect_double_top(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta padrão Double Top.
        """
        highs = self._find_peaks(df['high'], order=5)
        
        if len(highs) < 2:
            return None
        
        # Últimos dois topos
        last_two_highs = highs[-2:]
        
        # Topos em níveis similares (±2%)
        diff = abs(last_two_highs[0][1] - last_two_highs[1][1]) / last_two_highs[0][1]
        
        if diff < 0.02:
            return {
                "type": ChartPattern.DOUBLE_TOP.value,
                "direction": "BEARISH",
                "strength": 75,
                "confidence": 70,
                "target": self._calculate_pattern_target(df, "DOUBLE_TOP", last_two_highs)
            }
        
        return None
    
    def _detect_double_bottom(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta padrão Double Bottom.
        """
        lows = self._find_troughs(df['low'], order=5)
        
        if len(lows) < 2:
            return None
        
        # Últimos dois fundos
        last_two_lows = lows[-2:]
        
        # Fundos em níveis similares (±2%)
        diff = abs(last_two_lows[0][1] - last_two_lows[1][1]) / last_two_lows[0][1]
        
        if diff < 0.02:
            return {
                "type": ChartPattern.DOUBLE_BOTTOM.value,
                "direction": "BULLISH",
                "strength": 75,
                "confidence": 70,
                "target": self._calculate_pattern_target(df, "DOUBLE_BOTTOM", last_two_lows)
            }
        
        return None
    
    def _detect_triangle(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta padrões de triângulo (ascending, descending, symmetrical).
        """
        if len(df) < 30:
            return None
        
        recent_data = df.tail(30)
        
        # Topos e fundos
        highs = self._find_peaks(recent_data['high'], order=3)
        lows = self._find_troughs(recent_data['low'], order=3)
        
        if len(highs) < 2 or len(lows) < 2:
            return None
        
        # Slopes
        high_slope = self._calculate_slope([h[1] for h in highs])
        low_slope = self._calculate_slope([l[1] for l in lows])
        
        # Ascending Triangle (topos planos, fundos subindo)
        if abs(high_slope) < 0.0005 and low_slope > 0.001:
            return {
                "type": ChartPattern.TRIANGLE_ASCENDING.value,
                "direction": "BULLISH",
                "strength": 70,
                "confidence": 65
            }
        
        # Descending Triangle (fundos planos, topos descendo)
        if abs(low_slope) < 0.0005 and high_slope < -0.001:
            return {
                "type": ChartPattern.TRIANGLE_DESCENDING.value,
                "direction": "BEARISH",
                "strength": 70,
                "confidence": 65
            }
        
        # Symmetrical Triangle
        if low_slope > 0.0005 and high_slope < -0.0005:
            return {
                "type": ChartPattern.TRIANGLE_SYMMETRICAL.value,
                "direction": "NEUTRAL",
                "strength": 60,
                "confidence": 60
            }
        
        return None
    
    def _detect_channel(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta canais de preço.
        """
        if len(df) < 50:
            return None
        
        recent_data = df.tail(50)
        
        # Linear regression nos topos e fundos
        highs = self._find_peaks(recent_data['high'], order=5)
        lows = self._find_troughs(recent_data['low'], order=5)
        
        if len(highs) < 3 or len(lows) < 3:
            return None
        
        high_slope = self._calculate_slope([h[1] for h in highs])
        low_slope = self._calculate_slope([l[1] for l in lows])
        
        # Channel Up
        if high_slope > 0.001 and low_slope > 0.001:
            slope_diff = abs(high_slope - low_slope)
            if slope_diff < 0.0005:  # Slopes paralelos
                return {
                    "type": ChartPattern.CHANNEL_UP.value,
                    "direction": "BULLISH",
                    "strength": 65,
                    "confidence": 60
                }
        
        # Channel Down
        if high_slope < -0.001 and low_slope < -0.001:
            slope_diff = abs(high_slope - low_slope)
            if slope_diff < 0.0005:  # Slopes paralelos
                return {
                    "type": ChartPattern.CHANNEL_DOWN.value,
                    "direction": "BEARISH",
                    "strength": 65,
                    "confidence": 60
                }
        
        return None
    
    def _find_peaks(self, series: pd.Series, order: int = 5) -> List[Tuple[int, float]]:
        """
        Encontra picos locais.
        """
        peaks = []
        for i in range(order, len(series) - order):
            if all(series.iloc[i] >= series.iloc[i-j] for j in range(1, order+1)) and \
               all(series.iloc[i] >= series.iloc[i+j] for j in range(1, order+1)):
                peaks.append((i, series.iloc[i]))
        return peaks
    
    def _find_troughs(self, series: pd.Series, order: int = 5) -> List[Tuple[int, float]]:
        """
        Encontra vales locais.
        """
        troughs = []
        for i in range(order, len(series) - order):
            if all(series.iloc[i] <= series.iloc[i-j] for j in range(1, order+1)) and \
               all(series.iloc[i] <= series.iloc[i+j] for j in range(1, order+1)):
                troughs.append((i, series.iloc[i]))
        return troughs
    
    def _calculate_slope(self, values: List[float]) -> float:
        """
        Calcula slope (inclinação) de uma série de valores.
        """
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        slope = np.polyfit(x, y, 1)[0]
        return float(slope)
    
    def _calculate_pattern_target(self, df: pd.DataFrame, pattern_type: str, points: List) -> float:
        """
        Calcula target de preço baseado no padrão.
        """
        current_price = df['close'].iloc[-1]
        
        if pattern_type == "DOUBLE_TOP":
            height = points[0][1] - df['low'].tail(20).min()
            return current_price - height
        
        elif pattern_type == "DOUBLE_BOTTOM":
            height = df['high'].tail(20).max() - points[0][1]
            return current_price + height
        
        return current_price
    
    def _analyze_price_action(self, df: pd.DataFrame) -> Dict:
        """
        Análise de price action pura.
        """
        if len(df) < 10:
            return {}
        
        last_candles = df.tail(10)
        
        # Sequência de topos e fundos
        highs_increasing = all(
            last_candles['high'].iloc[i] >= last_candles['high'].iloc[i-1] 
            for i in range(1, min(5, len(last_candles)))
        )
        
        lows_increasing = all(
            last_candles['low'].iloc[i] >= last_candles['low'].iloc[i-1] 
            for i in range(1, min(5, len(last_candles)))
        )
        
        highs_decreasing = all(
            last_candles['high'].iloc[i] <= last_candles['high'].iloc[i-1] 
            for i in range(1, min(5, len(last_candles)))
        )
        
        lows_decreasing = all(
            last_candles['low'].iloc[i] <= last_candles['low'].iloc[i-1] 
            for i in range(1, min(5, len(last_candles)))
        )
        
        # Classificação
        if highs_increasing and lows_increasing:
            trend_type = "STRONG_UPTREND"
        elif highs_decreasing and lows_decreasing:
            trend_type = "STRONG_DOWNTREND"
        elif highs_increasing and not lows_increasing:
            trend_type = "BULLISH_CONSOLIDATION"
        elif highs_decreasing and not lows_decreasing:
            trend_type = "BEARISH_CONSOLIDATION"
        else:
            trend_type = "RANGING"
        
        return {
            "trend_type": trend_type,
            "highs_increasing": highs_increasing,
            "lows_increasing": lows_increasing,
            "highs_decreasing": highs_decreasing,
            "lows_decreasing": lows_decreasing
        }
    
    def _detect_breakouts(self, df: pd.DataFrame, sr_levels: Dict) -> List[Dict]:
        """
        Detecta breakouts de suporte/resistência.
        """
        breakouts = []
        
        if not sr_levels or len(df) < 5:
            return breakouts
        
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        
        # Resistances
        for resistance in sr_levels.get('resistance', []):
            if prev_price < resistance and current_price > resistance:
                breakouts.append({
                    "type": "RESISTANCE_BREAKOUT",
                    "direction": "BULLISH",
                    "level": resistance,
                    "strength": 70,
                    "volume_confirmation": self._check_volume_spike(df)
                })
        
        # Supports
        for support in sr_levels.get('support', []):
            if prev_price > support and current_price < support:
                breakouts.append({
                    "type": "SUPPORT_BREAKDOWN",
                    "direction": "BEARISH",
                    "level": support,
                    "strength": 70,
                    "volume_confirmation": self._check_volume_spike(df)
                })
        
        return breakouts
    
    def _detect_reversals(self, df_m15: pd.DataFrame, df_h1: pd.DataFrame) -> List[Dict]:
        """
        Detecta sinais de reversão.
        """
        reversals = []
        
        # Divergência RSI
        rsi_divergence = self._check_rsi_divergence(df_h1)
        if rsi_divergence:
            reversals.append(rsi_divergence)
        
        # Padrões de reversão em suporte/resistência
        # (já implementado em candle_patterns)
        
        return reversals
    
    def _detect_continuations(self, df_m15: pd.DataFrame, df_h1: pd.DataFrame) -> List[Dict]:
        """
        Detecta sinais de continuação.
        """
        continuations = []
        
        # Pullback em tendência
        if self._is_healthy_pullback(df_m15, df_h1):
            continuations.append({
                "type": "PULLBACK_CONTINUATION",
                "direction": self._get_trend_direction(df_h1),
                "strength": 70
            })
        
        return continuations
    
    def _check_volume_spike(self, df: pd.DataFrame) -> bool:
        """
        Verifica se houve spike de volume.
        """
        if 'volume' not in df.columns or len(df) < 20:
            return False
        
        avg_vol = df['volume'].tail(20).mean()
        current_vol = df['volume'].iloc[-1]
        
        return current_vol > avg_vol * 1.5
    
    def _check_rsi_divergence(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta divergências de RSI.
        """
        if len(df) < 30:
            return None
        
        # Implementação simplificada
        # Em produção, usar algoritmo mais robusto
        
        return None
    
    def _is_healthy_pullback(self, df_m15: pd.DataFrame, df_h1: pd.DataFrame) -> bool:
        """
        Verifica se é um pullback saudável.
        """
        if len(df_m15) < 20 or len(df_h1) < 50:
            return False
        
        # Tendência clara em H1
        trend = self._get_trend_direction(df_h1)
        if trend == "NEUTRAL":
            return False
        
        # Retração em M15 mas sem quebrar estrutura
        recent_move = df_m15['close'].iloc[-5:].pct_change().sum()
        
        if trend == "BULLISH" and -0.015 < recent_move < -0.003:
            return True
        
        if trend == "BEARISH" and 0.003 < recent_move < 0.015:
            return True
        
        return False
    
    def _get_trend_direction(self, df: pd.DataFrame) -> str:
        """
        Determina direção da tendência.
        """
        if len(df) < 50:
            return "NEUTRAL"
        
        ema_50 = df['close'].ewm(span=50).mean()
        current_price = df['close'].iloc[-1]
        
        if current_price > ema_50.iloc[-1] * 1.005:
            return "BULLISH"
        elif current_price < ema_50.iloc[-1] * 0.995:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_pattern_quality(self, patterns: Dict) -> int:
        """
        Calcula score de qualidade agregado dos padrões.
        """
        score = 0
        count = 0
        
        # Candle patterns
        for tf, pats in patterns["candle_patterns"].items():
            for pat in pats:
                score += pat["strength"] * pat["confidence"] / 100
                count += 1
        
        # Chart patterns
        for tf, pats in patterns["chart_patterns"].items():
            for pat in pats:
                score += pat["strength"] * pat["confidence"] / 100
                count += 1
        
        # Breakouts
        for breakout in patterns["breakout_signals"]:
            score += breakout["strength"]
            count += 1
        
        if count == 0:
            return 0
        
        return int(score / count)
    
    def _determine_primary_signal(self, patterns: Dict) -> Optional[Dict]:
        """
        Determina o sinal primário mais forte.
        """
        all_signals = []
        
        # Agregar todos os sinais
        for tf, pats in patterns["candle_patterns"].items():
            for pat in pats:
                all_signals.append({
                    **pat,
                    "source": f"candle_{tf}",
                    "composite_score": pat["strength"] * pat["confidence"] / 100
                })
        
        for tf, pats in patterns["chart_patterns"].items():
            for pat in pats:
                all_signals.append({
                    **pat,
                    "source": f"chart_{tf}",
                    "composite_score": pat["strength"] * pat["confidence"] / 100
                })
        
        for breakout in patterns["breakout_signals"]:
            all_signals.append({
                **breakout,
                "source": "breakout",
                "composite_score": breakout["strength"]
            })
        
        if not all_signals:
            return None
        
        # Retorna o sinal com maior composite_score
        return max(all_signals, key=lambda x: x["composite_score"])


if __name__ == "__main__":
    print("Pattern Engine - Sistema de Detecção de Padrões")
    print("Módulo pronto para integração")
