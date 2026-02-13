"""
═══════════════════════════════════════════════════════════════════
CAMADA 12: APRENDIZADO POR SIMILARIDADE
═══════════════════════════════════════════════════════════════════
O bot encontra situações históricas parecidas e usa como referência.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta
from core.logger import get_logger


@dataclass
class SimilarityMatch:
    """Representação de um match histórico similar"""
    historical_trade_id: str
    similarity_score: float  # 0-1
    context: Dict
    outcome: str  # WIN/LOSE
    confidence: float
    pnl: float


class SimilarityMatcher:
    """
    Sistema de busca por padrões históricos similares.
    
    Princípio: Usar histórico real como validação.
    """
    
    def __init__(self, memory_engine=None):
        self.logger = get_logger()
        self.memory = memory_engine
        
        # Pesos de similaridade
        self.similarity_weights = {
            "trend_direction": 0.20,
            "volatility_level": 0.15,
            "market_structure": 0.15,
            "pattern_type": 0.20,
            "session": 0.10,
            "momentum": 0.10,
            "liquidity": 0.10
        }
        
        # Thresholds
        self.min_similarity_score = 0.75
        self.historical_lookback_days = 90
    
    def find_similar_situations(
        self,
        current_context: Dict,
        current_market: Dict,
        current_pattern: str,
        top_n: int = 5
    ) -> List[SimilarityMatch]:
        """
        Encontra N situações históricas similares à atual.
        """
        if not self.memory:
            return []
        
        # Obter histórico
        trades = self.memory.get_trades_from_days_ago(self.historical_lookback_days)
        if not trades:
            return []
        
        matches = []
        
        # Calcular similaridade com cada trade histórico
        for trade in trades:
            similarity_score = self._calculate_similarity(
                current_context,
                current_market,
                current_pattern,
                trade
            )
            
            if similarity_score >= self.min_similarity_score:
                match = SimilarityMatch(
                    historical_trade_id=trade.id,
                    similarity_score=similarity_score,
                    context=trade.context,
                    outcome="WIN" if trade.pnl > 0 else "LOSE",
                    confidence=self._calculate_confidence(trade),
                    pnl=trade.pnl
                )
                matches.append(match)
        
        # Ordenar por similaridade
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return matches[:top_n]
    
    def _calculate_similarity(
        self,
        current_context: Dict,
        current_market: Dict,
        current_pattern: str,
        historical_trade: Dict
    ) -> float:
        """
        Calcula score de similaridade entre situação atual e histórica.
        """
        scores = {}
        
        # 1. Similaridade de direção de tendência
        try:
            current_trend = current_market.get("trend", {}).get("consensus", {}).get("direction")
            historical_trend = historical_trade.context.get("trend_direction")
            
            trend_sim = 1.0 if current_trend == historical_trend else 0.3
            scores["trend_direction"] = trend_sim
        except:
            scores["trend_direction"] = 0.5
        
        # 2. Similaridade de volatilidade
        try:
            current_vol = current_market.get("volatility", {}).get("classification")
            historical_vol = historical_trade.context.get("volatility_level")
            
            vol_sim = 1.0 if current_vol == historical_vol else (
                0.7 if abs(self._vol_to_num(current_vol) - self._vol_to_num(historical_vol)) <= 1 else 0.3
            )
            scores["volatility_level"] = vol_sim
        except:
            scores["volatility_level"] = 0.5
        
        # 3. Similaridade de estrutura (HH/HL/LH/LL)
        try:
            current_struct = current_market.get("structure", {}).get("strength", 0)
            historical_struct = historical_trade.context.get("market_structure", 0)
            
            struct_sim = 1.0 - abs(current_struct - historical_struct) / 100
            scores["market_structure"] = max(0, struct_sim)
        except:
            scores["market_structure"] = 0.5
        
        # 4. Similaridade de padrão
        try:
            current_pattern_type = current_pattern.split("_")[0] if "_" in current_pattern else current_pattern
            historical_pattern = historical_trade.context.get("pattern_type", "").split("_")[0]
            
            pattern_sim = 0.9 if current_pattern_type.lower() == historical_pattern.lower() else 0.4
            scores["pattern_type"] = pattern_sim
        except:
            scores["pattern_type"] = 0.5
        
        # 5. Similaridade de sessão
        try:
            current_session = current_market.get("session", {}).get("current")
            historical_session = historical_trade.context.get("session")
            
            session_sim = 1.0 if current_session == historical_session else 0.5
            scores["session"] = session_sim
        except:
            scores["session"] = 0.5
        
        # 6. Similaridade de momentum
        try:
            current_mom = current_market.get("momentum", {}).get("score", 50) / 100
            historical_mom = historical_trade.context.get("momentum", 0.5)
            
            mom_sim = 1.0 - abs(current_mom - historical_mom)
            scores["momentum"] = max(0, mom_sim)
        except:
            scores["momentum"] = 0.5
        
        # 7. Similaridade de liquidez
        try:
            current_liq = current_market.get("liquidity", {}).get("score", 50) / 100
            historical_liq = historical_trade.context.get("liquidity", 0.5)
            
            liq_sim = 1.0 - abs(current_liq - historical_liq)
            scores["liquidity"] = max(0, liq_sim)
        except:
            scores["liquidity"] = 0.5
        
        # Calcular score ponderado
        weighted_score = sum(
            scores.get(key, 0.5) * weight
            for key, weight in self.similarity_weights.items()
        )
        
        return weighted_score
    
    def _vol_to_num(self, vol_class: str) -> int:
        """Converte classe de volatilidade para número"""
        mapping = {"LOW": 0, "NORMAL": 1, "HIGH": 2}
        return mapping.get(vol_class, 1)
    
    def _calculate_confidence(self, trade: Dict) -> float:
        """
        Calcula confiança no match histórico.
        Baseado em: recência, sequência de wins, R-múltiplos
        """
        confidence = 0.5
        
        # Trades recentes têm mais confiança
        days_ago = (datetime.now() - datetime.fromisoformat(trade.entry_time)).days
        recency_factor = 1.0 - (days_ago / 90)  # Vai de 1 (hoje) para 0 (90 dias)
        confidence += recency_factor * 0.30
        
        # Trades com bom R-múltiplo têm mais confiança
        try:
            r_multiple = trade.pnl / trade.risk if trade.risk > 0 else 0
            if r_multiple > 2:
                confidence += 0.20
            elif r_multiple > 1:
                confidence += 0.10
        except:
            pass
        
        return min(1.0, confidence)
    
    def analyze_similar_outcomes(self, matches: List[SimilarityMatch]) -> Dict:
        """
        Analisa resultados dos matches similares.
        """
        if not matches:
            return {"warning": "No similar patterns found"}
        
        wins = sum(1 for m in matches if m.outcome == "WIN")
        loses = sum(1 for m in matches if m.outcome == "LOSE")
        total = len(matches)
        
        win_rate = wins / total if total > 0 else 0
        avg_pnl = np.mean([m.pnl for m in matches])
        
        return {
            "total_matches": total,
            "win_rate": win_rate,
            "wins": wins,
            "loses": loses,
            "avg_pnl": avg_pnl,
            "avg_similarity": np.mean([m.similarity_score for m in matches]),
            "recommendation": self._get_recommendation(win_rate, avg_pnl),
            "details": [
                {
                    "id": m.historical_trade_id,
                    "similarity": m.similarity_score,
                    "outcome": m.outcome,
                    "pnl": m.pnl,
                    "confidence": m.confidence
                }
                for m in matches[:3]  # Top 3
            ]
        }
    
    def _get_recommendation(self, win_rate: float, avg_pnl: float) -> str:
        """
        Recomendação baseada em análise histórica.
        """
        if win_rate < 0.40:
            return "BLOCK_TRADE"
        elif win_rate < 0.50:
            return "CAUTION_REQUIRED"
        elif win_rate >= 0.60 and avg_pnl > 0:
            return "STRONG_BUY_SIGNAL"
        elif win_rate >= 0.55:
            return "APPROVE_WITH_CAUTION"
        else:
            return "NEUTRAL"
    
    def should_trade_be_blocked(self, matches: List[SimilarityMatch]) -> Tuple[bool, str]:
        """
        Determina se um trade deve ser bloqueado por histórico negativo.
        """
        if not matches:
            return False, "Insufficient historical data"
        
        analysis = self.analyze_similar_outcomes(matches)
        
        if analysis["recommendation"] == "BLOCK_TRADE":
            return True, f"Similar pattern has {analysis['win_rate']:.0%} win rate (below 40%)"
        
        return False, "Historical data supports trade"
    
    def get_similarity_report(self, matches: List[SimilarityMatch]) -> Dict:
        """Relatório completo de similaridade"""
        if not matches:
            return {"status": "No similar patterns found"}
        
        analysis = self.analyze_similar_outcomes(matches)
        
        return {
            "status": "Similar patterns found",
            "analysis": analysis,
            "top_match": {
                "id": matches[0].historical_trade_id,
                "similarity": matches[0].similarity_score,
                "outcome": matches[0].outcome,
                "pnl": matches[0].pnl
            } if matches else None
        }
