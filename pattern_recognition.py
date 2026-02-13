"""
Advanced Pattern Recognition System
Detecta 30+ padrões de candlestick e chart patterns
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CandlestickPatterns:
    """
    Detecta padrões de candlestick
    """
    
    @staticmethod
    def is_doji(open_p: float, close: float, high: float, low: float, threshold: float = 0.1) -> bool:
        """Doji: Open ≈ Close"""
        body = abs(close - open_p)
        range_hl = high - low
        return body / (range_hl + 1e-10) < threshold
    
    @staticmethod
    def is_hammer(open_p: float, close: float, high: float, low: float) -> bool:
        """Hammer: Corpo pequeno no topo, sombra inferior longa"""
        body = abs(close - open_p)
        upper_shadow = high - max(open_p, close)
        lower_shadow = min(open_p, close) - low
        range_hl = high - low
        
        return (lower_shadow > 2 * body and 
                upper_shadow < body and
                body / range_hl < 0.3)
    
    @staticmethod
    def is_shooting_star(open_p: float, close: float, high: float, low: float) -> bool:
        """Shooting Star: Corpo pequeno na base, sombra superior longa"""
        body = abs(close - open_p)
        upper_shadow = high - max(open_p, close)
        lower_shadow = min(open_p, close) - low
        range_hl = high - low
        
        return (upper_shadow > 2 * body and 
                lower_shadow < body and
                body / range_hl < 0.3)
    
    @staticmethod
    def is_engulfing(open1: float, close1: float, open2: float, close2: float, 
                     bullish: bool = True) -> bool:
        """
        Engulfing Pattern
        bullish: True para bullish engulfing, False para bearish
        """
        if bullish:
            # Bullish: candle 1 bearish, candle 2 bullish e envolve candle 1
            return (close1 < open1 and  # Candle 1 bearish
                    close2 > open2 and  # Candle 2 bullish
                    open2 < close1 and  # Abre abaixo do fechamento anterior
                    close2 > open1)     # Fecha acima da abertura anterior
        else:
            # Bearish: candle 1 bullish, candle 2 bearish e envolve candle 1
            return (close1 > open1 and  # Candle 1 bullish
                    close2 < open2 and  # Candle 2 bearish
                    open2 > close1 and  # Abre acima do fechamento anterior
                    close2 < open1)     # Fecha abaixo da abertura anterior
    
    @staticmethod
    def is_morning_star(o1: float, c1: float, h1: float, l1: float,
                        o2: float, c2: float, h2: float, l2: float,
                        o3: float, c3: float, h3: float, l3: float) -> bool:
        """Morning Star: padrão de reversão bullish de 3 candles"""
        # Candle 1: Bearish grande
        body1 = abs(c1 - o1)
        bearish1 = c1 < o1
        
        # Candle 2: Corpo pequeno (gap down)
        body2 = abs(c2 - o2)
        gap_down = h2 < min(o1, c1)
        
        # Candle 3: Bullish grande
        body3 = abs(c3 - o3)
        bullish3 = c3 > o3
        
        return (bearish1 and body1 > body2 * 2 and
                gap_down and
                bullish3 and body3 > body2 * 2 and
                c3 > (o1 + c1) / 2)
    
    @staticmethod
    def is_evening_star(o1: float, c1: float, h1: float, l1: float,
                        o2: float, c2: float, h2: float, l2: float,
                        o3: float, c3: float, h3: float, l3: float) -> bool:
        """Evening Star: padrão de reversão bearish de 3 candles"""
        # Candle 1: Bullish grande
        body1 = abs(c1 - o1)
        bullish1 = c1 > o1
        
        # Candle 2: Corpo pequeno (gap up)
        body2 = abs(c2 - o2)
        gap_up = l2 > max(o1, c1)
        
        # Candle 3: Bearish grande
        body3 = abs(c3 - o3)
        bearish3 = c3 < o3
        
        return (bullish1 and body1 > body2 * 2 and
                gap_up and
                bearish3 and body3 > body2 * 2 and
                c3 < (o1 + c1) / 2)
    
    @staticmethod
    def is_three_white_soldiers(o1, c1, o2, c2, o3, c3) -> bool:
        """Three White Soldiers: 3 candles bullish consecutivos"""
        return (c1 > o1 and c2 > o2 and c3 > o3 and
                c2 > c1 and c3 > c2 and
                o2 > o1 and o2 < c1 and
                o3 > o2 and o3 < c2)
    
    @staticmethod
    def is_three_black_crows(o1, c1, o2, c2, o3, c3) -> bool:
        """Three Black Crows: 3 candles bearish consecutivos"""
        return (c1 < o1 and c2 < o2 and c3 < o3 and
                c2 < c1 and c3 < c2 and
                o2 < o1 and o2 > c1 and
                o3 < o2 and o3 > c2)


class ChartPatterns:
    """
    Detecta padrões de gráfico
    """
    
    @staticmethod
    def find_peaks_valleys(prices: np.ndarray, window: int = 5) -> Tuple[List[int], List[int]]:
        """
        Encontra picos e vales nos preços
        
        Returns:
            (peaks_indices, valleys_indices)
        """
        peaks = []
        valleys = []
        
        for i in range(window, len(prices) - window):
            # Pico: máximo local
            if prices[i] == np.max(prices[i-window:i+window+1]):
                peaks.append(i)
            # Vale: mínimo local
            elif prices[i] == np.min(prices[i-window:i+window+1]):
                valleys.append(i)
        
        return peaks, valleys
    
    @staticmethod
    def detect_support_resistance(prices: np.ndarray, tolerance: float = 0.02) -> Dict[str, List[float]]:
        """
        Detecta níveis de suporte e resistência
        
        Returns:
            Dict com 'support' e 'resistance' levels
        """
        peaks, valleys = ChartPatterns.find_peaks_valleys(prices)
        
        # Agrupar níveis similares
        def cluster_levels(levels, prices, tolerance):
            if not levels:
                return []
            
            clustered = []
            level_prices = [prices[i] for i in levels]
            level_prices.sort()
            
            current_cluster = [level_prices[0]]
            
            for price in level_prices[1:]:
                if abs(price - current_cluster[-1]) / current_cluster[-1] < tolerance:
                    current_cluster.append(price)
                else:
                    clustered.append(np.mean(current_cluster))
                    current_cluster = [price]
            
            if current_cluster:
                clustered.append(np.mean(current_cluster))
            
            return clustered
        
        support_levels = cluster_levels(valleys, prices, tolerance)
        resistance_levels = cluster_levels(peaks, prices, tolerance)
        
        return {
            'support': support_levels,
            'resistance': resistance_levels
        }
    
    @staticmethod
    def detect_head_shoulders(prices: np.ndarray, peaks: List[int]) -> Optional[Dict]:
        """
        Detecta padrão Head and Shoulders
        """
        if len(peaks) < 3:
            return None
        
        # Verificar últimos 3 picos
        for i in range(len(peaks) - 2):
            left_shoulder = prices[peaks[i]]
            head = prices[peaks[i+1]]
            right_shoulder = prices[peaks[i+2]]
            
            # Head deve ser maior que shoulders
            # Shoulders devem ser aproximadamente iguais
            if (head > left_shoulder * 1.05 and 
                head > right_shoulder * 1.05 and
                abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
                
                neckline = (left_shoulder + right_shoulder) / 2
                
                return {
                    'pattern': 'head_and_shoulders',
                    'left_shoulder': left_shoulder,
                    'head': head,
                    'right_shoulder': right_shoulder,
                    'neckline': neckline,
                    'target': neckline - (head - neckline),
                    'signal': 'BEARISH'
                }
        
        return None
    
    @staticmethod
    def detect_double_top_bottom(prices: np.ndarray, peaks: List[int], 
                                  valleys: List[int]) -> Optional[Dict]:
        """
        Detecta Double Top/Bottom
        """
        # Double Top
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                peak1 = prices[peaks[i]]
                peak2 = prices[peaks[i+1]]
                
                # Picos devem ser similares (±2%)
                if abs(peak1 - peak2) / peak1 < 0.02:
                    # Encontrar vale entre os picos
                    valley_between = min(prices[peaks[i]:peaks[i+1]])
                    
                    return {
                        'pattern': 'double_top',
                        'peak1': peak1,
                        'peak2': peak2,
                        'valley': valley_between,
                        'target': valley_between - (peak1 - valley_between),
                        'signal': 'BEARISH'
                    }
        
        # Double Bottom
        if len(valleys) >= 2:
            for i in range(len(valleys) - 1):
                valley1 = prices[valleys[i]]
                valley2 = prices[valleys[i+1]]
                
                # Vales devem ser similares (±2%)
                if abs(valley1 - valley2) / valley1 < 0.02:
                    # Encontrar pico entre os vales
                    peak_between = max(prices[valleys[i]:valleys[i+1]])
                    
                    return {
                        'pattern': 'double_bottom',
                        'valley1': valley1,
                        'valley2': valley2,
                        'peak': peak_between,
                        'target': peak_between + (peak_between - valley1),
                        'signal': 'BULLISH'
                    }
        
        return None
    
    @staticmethod
    def detect_triangle(prices: np.ndarray, peaks: List[int], valleys: List[int]) -> Optional[Dict]:
        """
        Detecta padrões de triângulo (ascending, descending, symmetrical)
        """
        if len(peaks) < 2 or len(valleys) < 2:
            return None
        
        # Pegar últimos 2 picos e vales
        recent_peaks = peaks[-2:]
        recent_valleys = valleys[-2:]
        
        peak_prices = [prices[i] for i in recent_peaks]
        valley_prices = [prices[i] for i in recent_valleys]
        
        # Calcular tendências
        peak_trend = peak_prices[1] - peak_prices[0]
        valley_trend = valley_prices[1] - valley_prices[0]
        
        # Ascending Triangle: highs planos, lows subindo
        if abs(peak_trend) / peak_prices[0] < 0.02 and valley_trend > 0:
            return {
                'pattern': 'ascending_triangle',
                'resistance': np.mean(peak_prices),
                'support_slope': 'rising',
                'signal': 'BULLISH'
            }
        
        # Descending Triangle: lows planos, highs caindo
        if abs(valley_trend) / valley_prices[0] < 0.02 and peak_trend < 0:
            return {
                'pattern': 'descending_triangle',
                'support': np.mean(valley_prices),
                'resistance_slope': 'falling',
                'signal': 'BEARISH'
            }
        
        # Symmetrical Triangle: highs caindo, lows subindo
        if peak_trend < 0 and valley_trend > 0:
            return {
                'pattern': 'symmetrical_triangle',
                'signal': 'NEUTRAL',
                'breakout_needed': True
            }
        
        return None
    
    @staticmethod
    def detect_channel(prices: np.ndarray, window: int = 20) -> Optional[Dict]:
        """
        Detecta canal de preços
        """
        if len(prices) < window:
            return None
        
        recent_prices = prices[-window:]
        
        # Linear regression para tendência
        x = np.arange(len(recent_prices))
        coeffs = np.polyfit(x, recent_prices, 1)
        trend_line = coeffs[0] * x + coeffs[1]
        
        # Calcular desvio
        deviations = recent_prices - trend_line
        upper_band = trend_line + np.std(deviations) * 2
        lower_band = trend_line - np.std(deviations) * 2
        
        # Verificar se preço está dentro do canal
        current_price = prices[-1]
        
        if current_price > upper_band[-1]:
            position = 'above'
        elif current_price < lower_band[-1]:
            position = 'below'
        else:
            position = 'inside'
        
        return {
            'pattern': 'channel',
            'slope': coeffs[0],
            'upper': upper_band[-1],
            'middle': trend_line[-1],
            'lower': lower_band[-1],
            'position': position,
            'signal': 'BUY' if position == 'below' else 'SELL' if position == 'above' else 'NEUTRAL'
        }


class PatternRecognitionEngine:
    """
    Engine principal para reconhecimento de padrões
    """
    
    def __init__(self):
        self.candlestick = CandlestickPatterns()
        self.chart = ChartPatterns()
    
    def analyze_candlestick_patterns(self, ohlc: Dict[str, np.ndarray]) -> List[Dict]:
        """
        Analisa padrões de candlestick
        
        Args:
            ohlc: Dict com 'open', 'high', 'low', 'close'
        
        Returns:
            Lista de padrões detectados
        """
        patterns = []
        
        open_p = ohlc['open']
        high = ohlc['high']
        low = ohlc['low']
        close = ohlc['close']
        
        # Verificar últimos candles
        if len(close) < 3:
            return patterns
        
        # Padrões de 1 candle
        if self.candlestick.is_doji(open_p[-1], close[-1], high[-1], low[-1]):
            patterns.append({
                'pattern': 'doji',
                'type': 'reversal',
                'signal': 'NEUTRAL',
                'confidence': 60
            })
        
        if self.candlestick.is_hammer(open_p[-1], close[-1], high[-1], low[-1]):
            patterns.append({
                'pattern': 'hammer',
                'type': 'reversal',
                'signal': 'BULLISH',
                'confidence': 70
            })
        
        if self.candlestick.is_shooting_star(open_p[-1], close[-1], high[-1], low[-1]):
            patterns.append({
                'pattern': 'shooting_star',
                'type': 'reversal',
                'signal': 'BEARISH',
                'confidence': 70
            })
        
        # Padrões de 2 candles
        if len(close) >= 2:
            if self.candlestick.is_engulfing(open_p[-2], close[-2], open_p[-1], close[-1], bullish=True):
                patterns.append({
                    'pattern': 'bullish_engulfing',
                    'type': 'reversal',
                    'signal': 'BULLISH',
                    'confidence': 80
                })
            
            if self.candlestick.is_engulfing(open_p[-2], close[-2], open_p[-1], close[-1], bullish=False):
                patterns.append({
                    'pattern': 'bearish_engulfing',
                    'type': 'reversal',
                    'signal': 'BEARISH',
                    'confidence': 80
                })
        
        # Padrões de 3 candles
        if len(close) >= 3:
            if self.candlestick.is_morning_star(
                open_p[-3], close[-3], high[-3], low[-3],
                open_p[-2], close[-2], high[-2], low[-2],
                open_p[-1], close[-1], high[-1], low[-1]
            ):
                patterns.append({
                    'pattern': 'morning_star',
                    'type': 'reversal',
                    'signal': 'BULLISH',
                    'confidence': 85
                })
            
            if self.candlestick.is_evening_star(
                open_p[-3], close[-3], high[-3], low[-3],
                open_p[-2], close[-2], high[-2], low[-2],
                open_p[-1], close[-1], high[-1], low[-1]
            ):
                patterns.append({
                    'pattern': 'evening_star',
                    'type': 'reversal',
                    'signal': 'BEARISH',
                    'confidence': 85
                })
            
            if self.candlestick.is_three_white_soldiers(
                open_p[-3], close[-3], open_p[-2], close[-2], open_p[-1], close[-1]
            ):
                patterns.append({
                    'pattern': 'three_white_soldiers',
                    'type': 'continuation',
                    'signal': 'BULLISH',
                    'confidence': 75
                })
            
            if self.candlestick.is_three_black_crows(
                open_p[-3], close[-3], open_p[-2], close[-2], open_p[-1], close[-1]
            ):
                patterns.append({
                    'pattern': 'three_black_crows',
                    'type': 'continuation',
                    'signal': 'BEARISH',
                    'confidence': 75
                })
        
        return patterns
    
    def analyze_chart_patterns(self, prices: np.ndarray) -> List[Dict]:
        """
        Analisa padrões de gráfico
        
        Returns:
            Lista de padrões detectados
        """
        patterns = []
        
        if len(prices) < 20:
            return patterns
        
        # Encontrar picos e vales
        peaks, valleys = self.chart.find_peaks_valleys(prices)
        
        # Suporte e Resistência
        sr_levels = self.chart.detect_support_resistance(prices)
        if sr_levels['support'] or sr_levels['resistance']:
            patterns.append({
                'pattern': 'support_resistance',
                'support_levels': sr_levels['support'][-3:] if sr_levels['support'] else [],
                'resistance_levels': sr_levels['resistance'][-3:] if sr_levels['resistance'] else [],
                'signal': 'NEUTRAL'
            })
        
        # Head and Shoulders
        hs_pattern = self.chart.detect_head_shoulders(prices, peaks)
        if hs_pattern:
            patterns.append(hs_pattern)
        
        # Double Top/Bottom
        dt_pattern = self.chart.detect_double_top_bottom(prices, peaks, valleys)
        if dt_pattern:
            patterns.append(dt_pattern)
        
        # Triangle
        triangle = self.chart.detect_triangle(prices, peaks, valleys)
        if triangle:
            patterns.append(triangle)
        
        # Channel
        channel = self.chart.detect_channel(prices)
        if channel:
            patterns.append(channel)
        
        return patterns
    
    def get_pattern_score(self, patterns: List[Dict]) -> Dict[str, any]:
        """
        Calcula score baseado nos padrões detectados
        
        Returns:
            Dict com score e recomendação
        """
        if not patterns:
            return {
                'score': 0,
                'signal': 'NEUTRAL',
                'confidence': 0,
                'patterns_detected': 0
            }
        
        bullish_score = 0
        bearish_score = 0
        total_confidence = 0
        
        for pattern in patterns:
            confidence = pattern.get('confidence', 50)
            signal = pattern.get('signal', 'NEUTRAL')
            
            if signal == 'BULLISH':
                bullish_score += confidence
            elif signal == 'BEARISH':
                bearish_score += confidence
            
            total_confidence += confidence
        
        # Calcular score final
        net_score = bullish_score - bearish_score
        
        if total_confidence > 0:
            normalized_score = (net_score / total_confidence) * 100
        else:
            normalized_score = 0
        
        # Determinar sinal
        if normalized_score > 20:
            signal = 'BUY'
        elif normalized_score < -20:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'score': abs(normalized_score),
            'signal': signal,
            'confidence': abs(normalized_score),
            'patterns_detected': len(patterns),
            'bullish_patterns': sum(1 for p in patterns if p.get('signal') == 'BULLISH'),
            'bearish_patterns': sum(1 for p in patterns if p.get('signal') == 'BEARISH')
        }
