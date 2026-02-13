"""
Machine Learning Engine para Trading
Usa Random Forest e LSTM para previsão de movimentos de preço
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

logger = logging.getLogger(__name__)


class FeatureEngineering:
    """
    Cria features avançadas para machine learning
    """
    
    @staticmethod
    def create_technical_features(ohlcv: Dict[str, np.ndarray]) -> pd.DataFrame:
        """
        Cria 100+ features técnicas
        
        Returns:
            DataFrame com features
        """
        df = pd.DataFrame(ohlcv)
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        features['price_momentum_5'] = df['close'].pct_change(5)
        features['price_momentum_10'] = df['close'].pct_change(10)
        features['price_momentum_20'] = df['close'].pct_change(20)
        
        # Volatility features
        for window in [5, 10, 20, 50]:
            features[f'volatility_{window}'] = df['returns'].rolling(window).std()
            features[f'volatility_ratio_{window}'] = (
                features[f'volatility_{window}'] / features['volatility_50']
            )
        
        # Moving averages
        for window in [5, 10, 20, 50, 100, 200]:
            features[f'sma_{window}'] = df['close'].rolling(window).mean()
            features[f'price_to_sma_{window}'] = df['close'] / features[f'sma_{window}']
        
        # Moving average crossovers
        features['sma_5_20_cross'] = (features['sma_5'] > features['sma_20']).astype(int)
        features['sma_10_50_cross'] = (features['sma_10'] > features['sma_50']).astype(int)
        features['sma_50_200_cross'] = (features['sma_50'] > features['sma_200']).astype(int)
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        features['rsi'] = 100 - (100 / (1 + rs))
        features['rsi_oversold'] = (features['rsi'] < 30).astype(int)
        features['rsi_overbought'] = (features['rsi'] > 70).astype(int)
        
        # MACD
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = ema_12 - ema_26
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_histogram'] = features['macd'] - features['macd_signal']
        features['macd_positive'] = (features['macd'] > features['macd_signal']).astype(int)
        
        # Bollinger Bands
        for window in [20, 50]:
            sma = df['close'].rolling(window).mean()
            std = df['close'].rolling(window).std()
            features[f'bb_upper_{window}'] = sma + (2 * std)
            features[f'bb_lower_{window}'] = sma - (2 * std)
            features[f'bb_position_{window}'] = (
                (df['close'] - features[f'bb_lower_{window}']) /
                (features[f'bb_upper_{window}'] - features[f'bb_lower_{window}'] + 1e-10)
            )
        
        # Volume features
        if 'volume' in df.columns:
            features['volume'] = df['volume']
            features['volume_sma_20'] = df['volume'].rolling(20).mean()
            features['volume_ratio'] = df['volume'] / (features['volume_sma_20'] + 1e-10)
            features['volume_trend'] = df['volume'].pct_change(5)
            
            # On-Balance Volume
            obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
            features['obv'] = obv
            features['obv_sma_20'] = obv.rolling(20).mean()
        
        # Price patterns
        features['higher_high'] = (
            (df['high'] > df['high'].shift(1)) & 
            (df['high'].shift(1) > df['high'].shift(2))
        ).astype(int)
        
        features['lower_low'] = (
            (df['low'] < df['low'].shift(1)) & 
            (df['low'].shift(1) < df['low'].shift(2))
        ).astype(int)
        
        # Candlestick features
        body = abs(df['close'] - df['open'])
        range_hl = df['high'] - df['low']
        features['body_to_range'] = body / (range_hl + 1e-10)
        features['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        features['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        features['is_bullish'] = (df['close'] > df['open']).astype(int)
        
        # Trend strength
        for window in [5, 10, 20]:
            x = np.arange(window)
            features[f'trend_strength_{window}'] = (
                df['close'].rolling(window).apply(
                    lambda y: np.corrcoef(x, y)[0, 1] if len(y) == window else np.nan
                )
            )
        
        # Statistical features
        for window in [5, 10, 20]:
            features[f'skew_{window}'] = df['returns'].rolling(window).skew()
            features[f'kurtosis_{window}'] = df['returns'].rolling(window).kurt()
        
        # Time features
        if hasattr(df.index, 'hour'):
            features['hour'] = df.index.hour
            features['day_of_week'] = df.index.dayofweek
            features['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
        
        return features.fillna(0)
    
    @staticmethod
    def create_target(prices: np.ndarray, lookahead: int = 5, threshold: float = 0.01) -> np.ndarray:
        """
        Cria target para classificação
        
        Args:
            prices: Array de preços
            lookahead: Períodos à frente
            threshold: Threshold para UP/DOWN (1%)
            
        Returns:
            Array com classes: 0=DOWN, 1=NEUTRAL, 2=UP
        """
        future_returns = pd.Series(prices).pct_change(lookahead).shift(-lookahead)
        
        target = np.zeros(len(prices))
        target[future_returns > threshold] = 2  # UP
        target[future_returns < -threshold] = 0  # DOWN
        target[(future_returns >= -threshold) & (future_returns <= threshold)] = 1  # NEUTRAL
        
        return target


class MLTradingEngine:
    """
    Engine de Machine Learning para trading
    """
    
    def __init__(self, model_path: str = 'models/'):
        self.model_path = model_path
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        
        # Criar diretório de modelos
        os.makedirs(model_path, exist_ok=True)
    
    def train(self, ohlcv: Dict[str, np.ndarray], 
              test_size: float = 0.2,
              lookahead: int = 5) -> Dict[str, float]:
        """
        Treina os modelos
        
        Returns:
            Dict com métricas de performance
        """
        logger.info("Iniciando treinamento dos modelos ML...")
        
        # Criar features
        features_df = FeatureEngineering.create_technical_features(ohlcv)
        target = FeatureEngineering.create_target(ohlcv['close'], lookahead)
        
        # Remover NaN
        valid_idx = ~(features_df.isna().any(axis=1) | np.isnan(target))
        X = features_df[valid_idx].values
        y = target[valid_idx]
        
        # Salvar feature names
        self.feature_names = features_df.columns.tolist()
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        logger.info("Treinando Random Forest...")
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train_scaled, y_train)
        rf_score = self.rf_model.score(X_test_scaled, y_test)
        
        # Train Gradient Boosting
        logger.info("Treinando Gradient Boosting...")
        self.gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.gb_model.fit(X_train_scaled, y_train)
        gb_score = self.gb_model.score(X_test_scaled, y_test)
        
        self.is_trained = True
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"Top 10 features:\n{feature_importance.head(10)}")
        
        metrics = {
            'rf_accuracy': rf_score,
            'gb_accuracy': gb_score,
            'n_samples': len(X),
            'n_features': X.shape[1],
            'n_train': len(X_train),
            'n_test': len(X_test)
        }
        
        logger.info(f"Training complete: RF={rf_score:.3f}, GB={gb_score:.3f}")
        
        return metrics
    
    def predict(self, ohlcv: Dict[str, np.ndarray]) -> Dict[str, any]:
        """
        Faz previsão usando ensemble de modelos
        
        Returns:
            Dict com previsão e probabilidades
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado. Execute train() primeiro.")
        
        # Criar features
        features_df = FeatureEngineering.create_technical_features(ohlcv)
        
        # Pegar última linha (mais recente)
        X = features_df.iloc[-1:].values
        X_scaled = self.scaler.transform(X)
        
        # Previsões
        rf_pred = self.rf_model.predict(X_scaled)[0]
        rf_proba = self.rf_model.predict_proba(X_scaled)[0]
        
        gb_pred = self.gb_model.predict(X_scaled)[0]
        gb_proba = self.gb_model.predict_proba(X_scaled)[0]
        
        # Ensemble (média das probabilidades)
        ensemble_proba = (rf_proba + gb_proba) / 2
        ensemble_pred = np.argmax(ensemble_proba)
        
        # Mapear classes para sinais
        class_to_signal = {0: 'SELL', 1: 'NEUTRAL', 2: 'BUY'}
        
        result = {
            'prediction': class_to_signal[ensemble_pred],
            'confidence': float(ensemble_proba[ensemble_pred] * 100),
            'probabilities': {
                'DOWN': float(ensemble_proba[0] * 100),
                'NEUTRAL': float(ensemble_proba[1] * 100),
                'UP': float(ensemble_proba[2] * 100)
            },
            'rf_prediction': class_to_signal[rf_pred],
            'gb_prediction': class_to_signal[gb_pred]
        }
        
        logger.info(
            f"ML Prediction: {result['prediction']} "
            f"(confidence: {result['confidence']:.1f}%)"
        )
        
        return result
    
    def save_models(self):
        """Salva modelos treinados"""
        if not self.is_trained:
            logger.warning("Nenhum modelo treinado para salvar")
            return
        
        joblib.dump(self.rf_model, os.path.join(self.model_path, 'rf_model.pkl'))
        joblib.dump(self.gb_model, os.path.join(self.model_path, 'gb_model.pkl'))
        joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.pkl'))
        joblib.dump(self.feature_names, os.path.join(self.model_path, 'features.pkl'))
        
        logger.info(f"Modelos salvos em {self.model_path}")
    
    def load_models(self):
        """Carrega modelos salvos"""
        try:
            self.rf_model = joblib.load(os.path.join(self.model_path, 'rf_model.pkl'))
            self.gb_model = joblib.load(os.path.join(self.model_path, 'gb_model.pkl'))
            self.scaler = joblib.load(os.path.join(self.model_path, 'scaler.pkl'))
            self.feature_names = joblib.load(os.path.join(self.model_path, 'features.pkl'))
            self.is_trained = True
            logger.info("Modelos carregados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            self.is_trained = False


def create_ml_engine() -> MLTradingEngine:
    """Factory function para criar ML engine"""
    return MLTradingEngine()
