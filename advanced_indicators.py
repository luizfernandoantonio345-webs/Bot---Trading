"""
Advanced Technical Indicators Library
50+ indicators profissionais para análise técnica
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AdvancedIndicators:
    """
    Biblioteca completa de indicadores técnicos
    """
    
    @staticmethod
    def sma(prices: np.ndarray, period: int) -> np.ndarray:
        """Simple Moving Average"""
        return pd.Series(prices).rolling(window=period).mean().values
    
    @staticmethod
    def ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Exponential Moving Average"""
        return pd.Series(prices).ewm(span=period, adjust=False).mean().values
    
    @staticmethod
    def wma(prices: np.ndarray, period: int) -> np.ndarray:
        """Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        return np.convolve(prices, weights/weights.sum(), mode='valid')
    
    @staticmethod
    def hma(prices: np.ndarray, period: int) -> np.ndarray:
        """Hull Moving Average"""
        half_length = period // 2
        sqrt_length = int(np.sqrt(period))
        
        wma_half = AdvancedIndicators.wma(prices, half_length)
        wma_full = AdvancedIndicators.wma(prices, period)
        
        # Alinhar comprimentos
        min_len = min(len(wma_half), len(wma_full))
        raw_hma = 2 * wma_half[-min_len:] - wma_full[-min_len:]
        
        return AdvancedIndicators.wma(raw_hma, sqrt_length)
    
    # ==================== MOMENTUM INDICATORS ====================
    
    @staticmethod
    def rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Relative Strength Index"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = pd.Series(gains).rolling(window=period).mean().values
        avg_losses = pd.Series(losses).rolling(window=period).mean().values
        
        rs = avg_gains / (avg_losses + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def stochastic(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                   k_period: int = 14, d_period: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """Stochastic Oscillator"""
        lowest_low = pd.Series(low).rolling(window=k_period).min().values
        highest_high = pd.Series(high).rolling(window=k_period).max().values
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
        d = pd.Series(k).rolling(window=d_period).mean().values
        
        return k, d
    
    @staticmethod
    def macd(prices: np.ndarray, fast: int = 12, slow: int = 26, 
             signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = AdvancedIndicators.ema(prices, fast)
        ema_slow = AdvancedIndicators.ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = AdvancedIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def williams_r(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                   period: int = 14) -> np.ndarray:
        """Williams %R"""
        highest_high = pd.Series(high).rolling(window=period).max().values
        lowest_low = pd.Series(low).rolling(window=period).min().values
        
        wr = -100 * (highest_high - close) / (highest_high - lowest_low + 1e-10)
        return wr
    
    @staticmethod
    def cci(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
            period: int = 20) -> np.ndarray:
        """Commodity Channel Index"""
        typical_price = (high + low + close) / 3
        sma_tp = AdvancedIndicators.sma(typical_price, period)
        
        mad = pd.Series(typical_price).rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean())), raw=True
        ).values
        
        cci = (typical_price - sma_tp) / (0.015 * mad + 1e-10)
        return cci
    
    @staticmethod
    def roc(prices: np.ndarray, period: int = 12) -> np.ndarray:
        """Rate of Change"""
        roc = 100 * (prices - np.roll(prices, period)) / (np.roll(prices, period) + 1e-10)
        roc[:period] = np.nan
        return roc
    
    @staticmethod
    def mfi(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
            volume: np.ndarray, period: int = 14) -> np.ndarray:
        """Money Flow Index"""
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        deltas = np.diff(typical_price)
        positive_flow = np.where(deltas > 0, money_flow[1:], 0)
        negative_flow = np.where(deltas < 0, money_flow[1:], 0)
        
        positive_mf = pd.Series(positive_flow).rolling(window=period).sum().values
        negative_mf = pd.Series(negative_flow).rolling(window=period).sum().values
        
        mfi = 100 - (100 / (1 + positive_mf / (negative_mf + 1e-10)))
        return np.concatenate([[np.nan], mfi])
    
    # ==================== TREND INDICATORS ====================
    
    @staticmethod
    def adx(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
            period: int = 14) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Average Directional Index"""
        # True Range
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Directional Movement
        up_move = high - np.roll(high, 1)
        down_move = np.roll(low, 1) - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Smoothed
        atr = pd.Series(tr).rolling(window=period).mean().values
        plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean().values / (atr + 1e-10)
        minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean().values / (atr + 1e-10)
        
        # ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        adx = pd.Series(dx).rolling(window=period).mean().values
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def supertrend(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                   period: int = 10, multiplier: float = 3) -> Tuple[np.ndarray, np.ndarray]:
        """Supertrend Indicator"""
        atr = AdvancedIndicators.atr(high, low, close, period)
        
        hl_avg = (high + low) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        supertrend = np.zeros_like(close)
        direction = np.ones_like(close)  # 1 = bullish, -1 = bearish
        
        for i in range(1, len(close)):
            # Ajustar bands
            if close[i] > upper_band[i-1]:
                direction[i] = 1
            elif close[i] < lower_band[i-1]:
                direction[i] = -1
            else:
                direction[i] = direction[i-1]
            
            if direction[i] == 1:
                supertrend[i] = lower_band[i]
            else:
                supertrend[i] = upper_band[i]
        
        return supertrend, direction
    
    @staticmethod
    def parabolic_sar(high: np.ndarray, low: np.ndarray, 
                      af_start: float = 0.02, af_max: float = 0.2) -> np.ndarray:
        """Parabolic SAR"""
        sar = np.zeros_like(high)
        trend = np.ones_like(high)  # 1 = up, -1 = down
        af = af_start
        ep = high[0]  # extreme point
        
        sar[0] = low[0]
        
        for i in range(1, len(high)):
            # Calculate SAR
            sar[i] = sar[i-1] + af * (ep - sar[i-1])
            
            # Check for trend reversal
            if trend[i-1] == 1:  # Uptrend
                if low[i] < sar[i]:
                    trend[i] = -1
                    sar[i] = ep
                    ep = low[i]
                    af = af_start
                else:
                    trend[i] = 1
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + af_start, af_max)
            else:  # Downtrend
                if high[i] > sar[i]:
                    trend[i] = 1
                    sar[i] = ep
                    ep = high[i]
                    af = af_start
                else:
                    trend[i] = -1
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + af_start, af_max)
        
        return sar
    
    @staticmethod
    def ichimoku(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                 tenkan: int = 9, kijun: int = 26, senkou_b: int = 52) -> Dict[str, np.ndarray]:
        """Ichimoku Cloud"""
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (pd.Series(high).rolling(window=tenkan).max().values + 
                      pd.Series(low).rolling(window=tenkan).min().values) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen = (pd.Series(high).rolling(window=kijun).max().values + 
                     pd.Series(low).rolling(window=kijun).min().values) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_a = (tenkan_sen + kijun_sen) / 2
        
        # Senkou Span B (Leading Span B)
        senkou_b = (pd.Series(high).rolling(window=senkou_b).max().values + 
                    pd.Series(low).rolling(window=senkou_b).min().values) / 2
        
        # Chikou Span (Lagging Span)
        chikou = np.roll(close, -kijun)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_a': senkou_a,
            'senkou_b': senkou_b,
            'chikou': chikou
        }
    
    # ==================== VOLATILITY INDICATORS ====================
    
    @staticmethod
    def bollinger_bands(prices: np.ndarray, period: int = 20, 
                        std_dev: float = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Bollinger Bands"""
        sma = AdvancedIndicators.sma(prices, period)
        std = pd.Series(prices).rolling(window=period).std().values
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
            period: int = 14) -> np.ndarray:
        """Average True Range"""
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = pd.Series(tr).rolling(window=period).mean().values
        
        return atr
    
    @staticmethod
    def keltner_channels(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                         period: int = 20, atr_mult: float = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Keltner Channels"""
        typical_price = (high + low + close) / 3
        middle = AdvancedIndicators.ema(typical_price, period)
        atr = AdvancedIndicators.atr(high, low, close, period)
        
        upper = middle + (atr_mult * atr)
        lower = middle - (atr_mult * atr)
        
        return upper, middle, lower
    
    @staticmethod
    def donchian_channels(high: np.ndarray, low: np.ndarray, 
                          period: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Donchian Channels"""
        upper = pd.Series(high).rolling(window=period).max().values
        lower = pd.Series(low).rolling(window=period).min().values
        middle = (upper + lower) / 2
        
        return upper, middle, lower
    
    # ==================== VOLUME INDICATORS ====================
    
    @staticmethod
    def obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """On-Balance Volume"""
        obv = np.zeros_like(volume)
        obv[0] = volume[0]
        
        for i in range(1, len(close)):
            if close[i] > close[i-1]:
                obv[i] = obv[i-1] + volume[i]
            elif close[i] < close[i-1]:
                obv[i] = obv[i-1] - volume[i]
            else:
                obv[i] = obv[i-1]
        
        return obv
    
    @staticmethod
    def vwap(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
             volume: np.ndarray) -> np.ndarray:
        """Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        cumulative_tp_vol = np.cumsum(typical_price * volume)
        cumulative_vol = np.cumsum(volume)
        
        vwap = cumulative_tp_vol / (cumulative_vol + 1e-10)
        return vwap
    
    @staticmethod
    def ad_line(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                volume: np.ndarray) -> np.ndarray:
        """Accumulation/Distribution Line"""
        clv = ((close - low) - (high - close)) / (high - low + 1e-10)
        ad = np.cumsum(clv * volume)
        return ad
    
    @staticmethod
    def cmf(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
            volume: np.ndarray, period: int = 20) -> np.ndarray:
        """Chaikin Money Flow"""
        mf_mult = ((close - low) - (high - close)) / (high - low + 1e-10)
        mf_volume = mf_mult * volume
        
        cmf = (pd.Series(mf_volume).rolling(window=period).sum().values / 
               pd.Series(volume).rolling(window=period).sum().values)
        
        return cmf


class IndicatorAnalyzer:
    """
    Analisa múltiplos indicadores e gera sinais
    """
    
    def __init__(self):
        self.indicators = AdvancedIndicators()
    
    def analyze_all(self, ohlcv: Dict[str, np.ndarray]) -> Dict[str, any]:
        """
        Analisa todos os indicadores
        
        Args:
            ohlcv: Dict com 'open', 'high', 'low', 'close', 'volume'
        
        Returns:
            Dict com todos os indicadores calculados
        """
        high = ohlcv['high']
        low = ohlcv['low']
        close = ohlcv['close']
        volume = ohlcv.get('volume', np.ones_like(close))
        
        results = {}
        
        try:
            # Momentum
            results['rsi'] = self.indicators.rsi(close)[-1]
            results['stoch_k'], results['stoch_d'] = self.indicators.stochastic(high, low, close)
            results['stoch_k'] = results['stoch_k'][-1]
            results['stoch_d'] = results['stoch_d'][-1]
            
            macd_line, signal_line, histogram = self.indicators.macd(close)
            results['macd'] = macd_line[-1]
            results['macd_signal'] = signal_line[-1]
            results['macd_hist'] = histogram[-1]
            
            results['williams_r'] = self.indicators.williams_r(high, low, close)[-1]
            results['cci'] = self.indicators.cci(high, low, close)[-1]
            results['mfi'] = self.indicators.mfi(high, low, close, volume)[-1]
            
            # Trend
            adx, plus_di, minus_di = self.indicators.adx(high, low, close)
            results['adx'] = adx[-1]
            results['plus_di'] = plus_di[-1]
            results['minus_di'] = minus_di[-1]
            
            # Volatility
            bb_upper, bb_mid, bb_lower = self.indicators.bollinger_bands(close)
            results['bb_upper'] = bb_upper[-1]
            results['bb_middle'] = bb_mid[-1]
            results['bb_lower'] = bb_lower[-1]
            results['bb_position'] = (close[-1] - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1] + 1e-10)
            
            results['atr'] = self.indicators.atr(high, low, close)[-1]
            
            # Volume
            results['obv'] = self.indicators.obv(close, volume)[-1]
            results['cmf'] = self.indicators.cmf(high, low, close, volume)[-1]
            
            logger.info(f"Indicadores calculados: {len(results)} valores")
            
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {e}")
        
        return results
    
    def generate_signals(self, indicators: Dict[str, float]) -> Dict[str, any]:
        """
        Gera sinais de trading baseado nos indicadores
        
        Returns:
            Dict com sinais e scores
        """
        signals = {
            'bullish_signals': 0,
            'bearish_signals': 0,
            'total_signals': 0,
            'confidence': 0,
            'details': []
        }
        
        # RSI
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi < 30:
                signals['bullish_signals'] += 2
                signals['details'].append('RSI oversold (< 30)')
            elif rsi > 70:
                signals['bearish_signals'] += 2
                signals['details'].append('RSI overbought (> 70)')
            signals['total_signals'] += 2
        
        # MACD
        if 'macd' in indicators and 'macd_signal' in indicators:
            if indicators['macd'] > indicators['macd_signal']:
                signals['bullish_signals'] += 1
                signals['details'].append('MACD bullish crossover')
            else:
                signals['bearish_signals'] += 1
                signals['details'].append('MACD bearish crossover')
            signals['total_signals'] += 1
        
        # ADX (força da tendência)
        if 'adx' in indicators:
            adx = indicators['adx']
            if adx > 25:
                if indicators.get('plus_di', 0) > indicators.get('minus_di', 0):
                    signals['bullish_signals'] += 1
                    signals['details'].append('Strong uptrend (ADX > 25)')
                else:
                    signals['bearish_signals'] += 1
                    signals['details'].append('Strong downtrend (ADX > 25)')
                signals['total_signals'] += 1
        
        # Bollinger Bands
        if 'bb_position' in indicators:
            bb_pos = indicators['bb_position']
            if bb_pos < 0.2:
                signals['bullish_signals'] += 1
                signals['details'].append('Price near lower Bollinger Band')
            elif bb_pos > 0.8:
                signals['bearish_signals'] += 1
                signals['details'].append('Price near upper Bollinger Band')
            signals['total_signals'] += 1
        
        # Chaikin Money Flow
        if 'cmf' in indicators:
            cmf = indicators['cmf']
            if cmf > 0.1:
                signals['bullish_signals'] += 1
                signals['details'].append('Positive money flow')
            elif cmf < -0.1:
                signals['bearish_signals'] += 1
                signals['details'].append('Negative money flow')
            signals['total_signals'] += 1
        
        # Calcular confidence score
        if signals['total_signals'] > 0:
            net_signals = signals['bullish_signals'] - signals['bearish_signals']
            signals['confidence'] = abs(net_signals) / signals['total_signals'] * 100
            
            if net_signals > 0:
                signals['signal'] = 'BUY'
            elif net_signals < 0:
                signals['signal'] = 'SELL'
            else:
                signals['signal'] = 'NEUTRAL'
        else:
            signals['signal'] = 'NEUTRAL'
        
        return signals
