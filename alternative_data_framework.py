"""
Alternative Data Framework for Trading
Sentiment analysis, news, social media, and other alternative data sources
"""

import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis for news and text"""
    
    def __init__(self):
        logger.info("Sentiment Analyzer initialized")
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text
            
        Returns:
            Sentiment analysis
        """
        # Placeholder for sentiment analysis
        # In production, use VADER, TextBlob, or transformer models
        
        # Simplified sentiment scoring
        positive_words = ['bullish', 'gain', 'profit', 'growth', 'rise', 'rally', 'surge', 'boom']
        negative_words = ['bearish', 'loss', 'decline', 'fall', 'crash', 'drop', 'plunge', 'recession']
        
        text_lower = text.lower()
        
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment (-1 to +1)
        total = positive_score + negative_score
        if total == 0:
            sentiment = 0.0
        else:
            sentiment = (positive_score - negative_score) / total
        
        return {
            'sentiment': sentiment,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'confidence': min(total / 10, 1.0)  # Confidence based on word count
        }


class NewsAnalyzer:
    """News sentiment and event analysis"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        logger.info("News Analyzer initialized")
    
    def analyze_news(self, news_articles: List[Dict]) -> Dict:
        """
        Analyze multiple news articles
        
        Args:
            news_articles: List of news articles with 'title' and 'content'
            
        Returns:
            Aggregated news sentiment
        """
        if not news_articles:
            return {
                'sentiment': 0.0,
                'confidence': 0.0,
                'article_count': 0
            }
        
        sentiments = []
        confidences = []
        
        for article in news_articles:
            text = f"{article.get('title', '')} {article.get('content', '')}"
            result = self.sentiment_analyzer.analyze_text(text)
            sentiments.append(result['sentiment'])
            confidences.append(result['confidence'])
        
        # Weighted average by confidence
        if sum(confidences) > 0:
            avg_sentiment = np.average(sentiments, weights=confidences)
        else:
            avg_sentiment = np.mean(sentiments)
        
        return {
            'sentiment': float(avg_sentiment),
            'confidence': float(np.mean(confidences)),
            'article_count': len(news_articles),
            'positive_articles': sum(1 for s in sentiments if s > 0.1),
            'negative_articles': sum(1 for s in sentiments if s < -0.1),
            'neutral_articles': sum(1 for s in sentiments if abs(s) <= 0.1)
        }
    
    def get_news_signal(self, symbol: str) -> Dict:
        """
        Get news sentiment signal for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            News signal
        """
        # Placeholder for fetching real news
        # In production, integrate with news APIs (NewsAPI, Alpha Vantage, etc.)
        
        # Simulate news articles
        sample_news = [
            {'title': f'{symbol} shows strong growth', 'content': 'The stock rallied on positive earnings'},
            {'title': f'Market outlook bullish for {symbol}', 'content': 'Analysts expect continued gains'},
        ]
        
        analysis = self.analyze_news(sample_news)
        
        # Generate signal
        if analysis['sentiment'] > 0.2:
            signal = 'BUY'
        elif analysis['sentiment'] < -0.2:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'signal': signal,
            'sentiment': analysis['sentiment'],
            'confidence': analysis['confidence'],
            'article_count': analysis['article_count']
        }


class SocialMediaAnalyzer:
    """Social media sentiment analysis"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        logger.info("Social Media Analyzer initialized")
    
    def analyze_tweets(self, tweets: List[str]) -> Dict:
        """
        Analyze sentiment from tweets
        
        Args:
            tweets: List of tweet texts
            
        Returns:
            Aggregated sentiment
        """
        if not tweets:
            return {'sentiment': 0.0, 'confidence': 0.0, 'tweet_count': 0}
        
        sentiments = []
        for tweet in tweets:
            result = self.sentiment_analyzer.analyze_text(tweet)
            sentiments.append(result['sentiment'])
        
        return {
            'sentiment': float(np.mean(sentiments)),
            'confidence': min(len(tweets) / 100, 1.0),  # More tweets = higher confidence
            'tweet_count': len(tweets),
            'bullish_tweets': sum(1 for s in sentiments if s > 0.1),
            'bearish_tweets': sum(1 for s in sentiments if s < -0.1)
        }
    
    def get_social_sentiment(self, symbol: str) -> Dict:
        """
        Get social media sentiment for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Social sentiment
        """
        # Placeholder for social media API
        # In production, integrate with Twitter API, Reddit API, etc.
        
        # Simulate tweets
        sample_tweets = [
            f'{symbol} to the moon! 🚀',
            f'Bullish on {symbol}, great fundamentals',
            f'{symbol} looks weak, might sell',
        ]
        
        analysis = self.analyze_tweets(sample_tweets)
        
        # Generate signal
        if analysis['sentiment'] > 0.15:
            signal = 'BUY'
        elif analysis['sentiment'] < -0.15:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'signal': signal,
            'sentiment': analysis['sentiment'],
            'confidence': analysis['confidence'],
            'tweet_count': analysis['tweet_count']
        }


class OrderFlowAnalyzer:
    """Order flow and market microstructure analysis"""
    
    def __init__(self):
        logger.info("Order Flow Analyzer initialized")
    
    def analyze_order_flow(self, order_book: Dict) -> Dict:
        """
        Analyze order flow imbalance
        
        Args:
            order_book: Order book data with bids and asks
            
        Returns:
            Order flow analysis
        """
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        if not bids or not asks:
            return {'imbalance': 0.0, 'signal': 'NEUTRAL', 'confidence': 0.0}
        
        # Calculate bid/ask volume
        bid_volume = sum(price * qty for price, qty in bids[:10])
        ask_volume = sum(price * qty for price, qty in asks[:10])
        
        # Calculate imbalance
        total_volume = bid_volume + ask_volume
        if total_volume > 0:
            imbalance = (bid_volume - ask_volume) / total_volume
        else:
            imbalance = 0.0
        
        # Generate signal
        if imbalance > 0.2:
            signal = 'BUY'
        elif imbalance < -0.2:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'imbalance': float(imbalance),
            'signal': signal,
            'confidence': min(abs(imbalance), 0.8),
            'bid_volume': bid_volume,
            'ask_volume': ask_volume
        }


class AlternativeDataSystem:
    """Complete alternative data system"""
    
    def __init__(self):
        self.news_analyzer = NewsAnalyzer()
        self.social_analyzer = SocialMediaAnalyzer()
        self.order_flow_analyzer = OrderFlowAnalyzer()
        
        logger.info("Alternative Data System initialized")
    
    def analyze_news_sentiment(self, symbol: str) -> Dict:
        """Get news sentiment for symbol"""
        return self.news_analyzer.get_news_signal(symbol)
    
    def analyze_social_sentiment(self, symbol: str) -> Dict:
        """Get social media sentiment for symbol"""
        return self.social_analyzer.get_social_sentiment(symbol)
    
    def analyze_order_flow(self, order_book: Dict) -> Dict:
        """Analyze order flow"""
        return self.order_flow_analyzer.analyze_order_flow(order_book)
    
    def get_combined_sentiment(self, symbol: str) -> Dict:
        """
        Get combined sentiment from all sources
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Combined sentiment analysis
        """
        # Get signals from all sources
        news = self.analyze_news_sentiment(symbol)
        social = self.analyze_social_sentiment(symbol)
        
        # Weighted combination
        news_weight = 0.6
        social_weight = 0.4
        
        combined_sentiment = (
            news['sentiment'] * news_weight +
            social['sentiment'] * social_weight
        )
        
        combined_confidence = (
            news['confidence'] * news_weight +
            social['confidence'] * social_weight
        )
        
        # Generate signal
        if combined_sentiment > 0.2:
            signal = 'BUY'
        elif combined_sentiment < -0.2:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'signal': signal,
            'sentiment': float(combined_sentiment),
            'confidence': float(combined_confidence),
            'news_sentiment': news['sentiment'],
            'social_sentiment': social['sentiment'],
            'breakdown': {
                'news': news,
                'social': social
            }
        }
    
    def combine_signals(self, signals: List[Dict], weights: Optional[List[float]] = None) -> Dict:
        """
        Combine multiple alternative data signals
        
        Args:
            signals: List of signal dictionaries
            weights: Optional weights for each signal
            
        Returns:
            Combined signal
        """
        if not signals:
            return {'signal': 'NEUTRAL', 'confidence': 0.0, 'score': 0.0}
        
        if weights is None:
            weights = [1.0 / len(signals)] * len(signals)
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Convert signals to scores
        signal_map = {'BUY': 1.0, 'NEUTRAL': 0.0, 'SELL': -1.0}
        
        scores = []
        confidences = []
        for signal_dict in signals:
            signal = signal_dict.get('signal', 'NEUTRAL')
            confidence = signal_dict.get('confidence', 0.0)
            
            scores.append(signal_map.get(signal, 0.0))
            confidences.append(confidence)
        
        # Weighted average
        combined_score = sum(s * w * c for s, w, c in zip(scores, weights, confidences))
        combined_confidence = sum(c * w for c, w in zip(confidences, weights))
        
        # Generate final signal
        if combined_score > 0.15:
            final_signal = 'BUY'
        elif combined_score < -0.15:
            final_signal = 'SELL'
        else:
            final_signal = 'NEUTRAL'
        
        return {
            'signal': final_signal,
            'score': float(combined_score),
            'confidence': float(combined_confidence),
            'individual_signals': signals
        }


def create_alternative_data_system() -> AlternativeDataSystem:
    """Factory function to create alternative data system"""
    return AlternativeDataSystem()


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("ALTERNATIVE DATA FRAMEWORK FOR TRADING")
    print("=" * 60)
    
    # Create system
    alt_system = create_alternative_data_system()
    
    # Example symbol
    symbol = "BTC/USDT"
    
    # Analyze news sentiment
    print(f"\n1. News Sentiment Analysis for {symbol}:")
    news_result = alt_system.analyze_news_sentiment(symbol)
    print(f"   Signal: {news_result['signal']}")
    print(f"   Sentiment: {news_result['sentiment']:.2f}")
    print(f"   Confidence: {news_result['confidence']:.2%}")
    print(f"   Articles analyzed: {news_result['article_count']}")
    
    # Analyze social sentiment
    print(f"\n2. Social Media Sentiment for {symbol}:")
    social_result = alt_system.analyze_social_sentiment(symbol)
    print(f"   Signal: {social_result['signal']}")
    print(f"   Sentiment: {social_result['sentiment']:.2f}")
    print(f"   Confidence: {social_result['confidence']:.2%}")
    print(f"   Tweets analyzed: {social_result['tweet_count']}")
    
    # Combined sentiment
    print(f"\n3. Combined Sentiment:")
    combined = alt_system.get_combined_sentiment(symbol)
    print(f"   Final Signal: {combined['signal']}")
    print(f"   Combined Sentiment: {combined['sentiment']:.2f}")
    print(f"   Confidence: {combined['confidence']:.2%}")
    print(f"   News weight: 60%, Social weight: 40%")
    
    # Order flow example
    print(f"\n4. Order Flow Analysis:")
    sample_order_book = {
        'bids': [(100, 10), (99.5, 20), (99, 15)],
        'asks': [(100.5, 8), (101, 12), (101.5, 10)]
    }
    flow_result = alt_system.analyze_order_flow(sample_order_book)
    print(f"   Signal: {flow_result['signal']}")
    print(f"   Imbalance: {flow_result['imbalance']:.2f}")
    print(f"   Confidence: {flow_result['confidence']:.2%}")
    
    print("\n✓ Alternative Data Framework ready for trading!")
