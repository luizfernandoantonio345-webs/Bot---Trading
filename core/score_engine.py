"""
═══════════════════════════════════════════════════════════════════
SCORE ENGINE - SISTEMA DE PONTUAÇÃO PROFISSIONAL (0-100)
═══════════════════════════════════════════════════════════════════
Avalia qualidade de oportunidades de trading com pesos calibrados.
Score < 65: NÃO OPERAR
Score 65-89: ALERTA APENAS
Score ≥ 90: EXECUÇÃO AUTOMÁTICA
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScoreWeights:
    """Pesos calibrados para cada componente do score."""
    trend: float = 0.25          # 25 pontos
    momentum: float = 0.20       # 20 pontos
    confirmations: float = 0.25  # 25 pontos
    risk_quality: float = 0.20   # 20 pontos
    context: float = 0.10        # 10 pontos


@dataclass
class ScoreResult:
    """Resultado completo do score."""
    total_score: int
    components: Dict[str, float]
    recommendation: str
    reasons: List[str]
    warnings: List[str]
    risk_reward_ratio: float
    confidence: float


class ScoreEngine:
    """
    Motor de pontuação profissional para decisões de trading.
    Avalia qualidade de setup com múltiplos critérios ponderados.
    """
    
    def __init__(self, custom_weights: Dict = None):
        """
        Inicializa engine com pesos personalizados opcionais.
        
        Args:
            custom_weights: Dict com pesos customizados (opcional)
        """
        if custom_weights:
            self.weights = ScoreWeights(**custom_weights)
        else:
            self.weights = ScoreWeights()
        
        self.score_history = []
        
        # Thresholds
        self.THRESHOLD_NO_TRADE = 65
        self.THRESHOLD_ALERT = 90
        self.MIN_RISK_REWARD = 1.5
    
    def calculate_comprehensive_score(
        self,
        market_analysis: Dict,
        pattern_analysis: Dict,
        risk_analysis: Dict,
        learning_insights: Dict = None
    ) -> ScoreResult:
        """
        Calcula score completo considerando todas as análises.
        
        Returns:
            ScoreResult com pontuação total e detalhes
        """
        
        components = {}
        reasons = []
        warnings = []
        
        # ═══════════════════════════════════
        # 1. TENDÊNCIA (25 pontos)
        # ═══════════════════════════════════
        trend_score = self._score_trend(market_analysis)
        components["trend"] = trend_score
        
        if trend_score >= 20:
            reasons.append(f"Tendência forte e clara ({trend_score:.1f}/25)")
        elif trend_score < 10:
            warnings.append("Tendência fraca ou indefinida")
        
        # ═══════════════════════════════════
        # 2. FORÇA DO MOVIMENTO (20 pontos)
        # ═══════════════════════════════════
        momentum_score = self._score_momentum(market_analysis)
        components["momentum"] = momentum_score
        
        if momentum_score >= 15:
            reasons.append(f"Momentum forte ({momentum_score:.1f}/20)")
        elif momentum_score < 8:
            warnings.append("Momentum fraco")
        
        # ═══════════════════════════════════
        # 3. CONFIRMAÇÕES TÉCNICAS (25 pontos)
        # ═══════════════════════════════════
        confirmation_score = self._score_confirmations(market_analysis, pattern_analysis)
        components["confirmations"] = confirmation_score
        
        if confirmation_score >= 20:
            reasons.append(f"Múltiplas confirmações técnicas ({confirmation_score:.1f}/25)")
        elif confirmation_score < 10:
            warnings.append("Poucas confirmações técnicas")
        
        # ═══════════════════════════════════
        # 4. QUALIDADE DE RISCO (20 pontos)
        # ═══════════════════════════════════
        risk_score = self._score_risk_quality(market_analysis, risk_analysis)
        components["risk"] = risk_score
        
        if risk_score >= 15:
            reasons.append(f"Risco controlado e favorável ({risk_score:.1f}/20)")
        elif risk_score < 8:
            warnings.append("Risco desfavorável")
        
        # ═══════════════════════════════════
        # 5. CONTEXTO TEMPORAL E HISTÓRICO (10 pontos)
        # ═══════════════════════════════════
        context_score = self._score_context(market_analysis, learning_insights)
        components["context"] = context_score
        
        if context_score >= 8:
            reasons.append(f"Contexto favorável ({context_score:.1f}/10)")
        elif context_score < 4:
            warnings.append("Contexto desfavorável")
        
        # ═══════════════════════════════════
        # SCORE TOTAL
        # ═══════════════════════════════════
        total_score = sum(components.values())
        
        # ═══════════════════════════════════
        # PENALIZAÇÃO POR HISTÓRICO NEGATIVO
        # ═══════════════════════════════════
        if learning_insights:
            penalty = self._calculate_learning_penalty(learning_insights)
            if penalty > 0:
                total_score -= penalty
                warnings.append(f"Penalização por histórico negativo: -{penalty}")
        
        # ═══════════════════════════════════
        # PENALIZAÇÃO SE RISCO > RETORNO
        # ═══════════════════════════════════
        risk_reward = self._calculate_risk_reward(risk_analysis)
        if risk_reward < self.MIN_RISK_REWARD:
            penalty = 15
            total_score -= penalty
            warnings.append(f"Risco/Retorno desfavorável: {risk_reward:.2f} < {self.MIN_RISK_REWARD}")
        
        # ═══════════════════════════════════
        # GARANTE LIMITES 0-100
        # ═══════════════════════════════════
        total_score = max(0, min(100, total_score))
        
        # ═══════════════════════════════════
        # RECOMENDAÇÃO
        # ═══════════════════════════════════
        recommendation = self._determine_recommendation(total_score, warnings)
        
        # ═══════════════════════════════════
        # CONFIANÇA
        # ═══════════════════════════════════
        confidence = self._calculate_confidence(components, warnings)
        
        result = ScoreResult(
            total_score=int(total_score),
            components=components,
            recommendation=recommendation,
            reasons=reasons,
            warnings=warnings,
            risk_reward_ratio=risk_reward,
            confidence=confidence
        )
        
        self.score_history.append({
            "timestamp": datetime.now(),
            "score": total_score,
            "recommendation": recommendation
        })
        
        return result
    
    def _score_trend(self, market_analysis: Dict) -> float:
        """
        Avalia qualidade da tendência (0-25 pontos).
        """
        score = 0.0
        max_score = 25.0
        
        trend = market_analysis.get("trend", {})
        
        # Consenso entre timeframes
        consensus = trend.get("consensus", {})
        consensus_direction = consensus.get("direction", "NEUTRAL")
        consensus_strength = consensus.get("strength", 0)
        
        if consensus_direction in ["BULLISH", "BEARISH"]:
            # Base score por consenso claro
            score += 10.0
            
            # Força do consenso
            score += (consensus_strength / 100) * 10.0
        else:
            # Sem consenso = score baixo
            score += 2.0
        
        # Alinhamento de EMAs
        h1_trend = trend.get("h1", {})
        if h1_trend.get("ema_alignment", False):
            score += 5.0
        
        return min(score, max_score)
    
    def _score_momentum(self, market_analysis: Dict) -> float:
        """
        Avalia força do momentum (0-20 pontos).
        """
        score = 0.0
        max_score = 20.0
        
        momentum = market_analysis.get("momentum", {})
        
        # Score do momentum
        momentum_score = momentum.get("score", 0)
        score += (momentum_score / 100) * 12.0
        
        # Direção clara
        direction = momentum.get("direction", "NEUTRAL")
        if direction != "NEUTRAL":
            score += 4.0
        
        # Força
        strength = momentum.get("strength", "WEAK")
        if strength == "STRONG":
            score += 4.0
        elif strength == "MODERATE":
            score += 2.0
        
        return min(score, max_score)
    
    def _score_confirmations(self, market_analysis: Dict, pattern_analysis: Dict) -> float:
        """
        Avalia confirmações técnicas (0-25 pontos).
        """
        score = 0.0
        max_score = 25.0
        
        # ═══════════════════════════════════
        # Estrutura de mercado
        # ═══════════════════════════════════
        structure = market_analysis.get("structure", {})
        structure_type = structure.get("type", "NEUTRAL")
        
        if structure_type in ["HIGHER_HIGH", "LOWER_LOW"]:
            score += 5.0
        elif structure_type in ["HIGHER_LOW", "LOWER_HIGH"]:
            score += 3.0
        
        # ═══════════════════════════════════
        # Padrões de candle
        # ═══════════════════════════════════
        candle_patterns = pattern_analysis.get("candle_patterns", {})
        
        strong_patterns = 0
        for tf, patterns in candle_patterns.items():
            for pattern in patterns:
                if pattern.get("strength", 0) >= 70:
                    strong_patterns += 1
        
        score += min(strong_patterns * 3, 9.0)
        
        # ═══════════════════════════════════
        # Padrões de gráfico
        # ═══════════════════════════════════
        chart_patterns = pattern_analysis.get("chart_patterns", {})
        
        for tf, patterns in chart_patterns.items():
            for pattern in patterns:
                if pattern.get("confidence", 0) >= 65:
                    score += 4.0
                    break  # Máximo 1 por timeframe
        
        # ═══════════════════════════════════
        # Volume confirmando
        # ═══════════════════════════════════
        volume = market_analysis.get("volume", {})
        if volume.get("available", False):
            if volume.get("trend_confirmation", False):
                score += 4.0
            elif volume.get("volume_ratio", 1.0) > 1.3:
                score += 2.0
        
        # ═══════════════════════════════════
        # Qualidade do movimento
        # ═══════════════════════════════════
        movement = market_analysis.get("movement_quality", {})
        if movement.get("classification") == "STRONG":
            score += 3.0
        
        return min(score, max_score)
    
    def _score_risk_quality(self, market_analysis: Dict, risk_analysis: Dict) -> float:
        """
        Avalia qualidade do risco (0-20 pontos).
        """
        score = 0.0
        max_score = 20.0
        
        # ═══════════════════════════════════
        # Volatilidade
        # ═══════════════════════════════════
        volatility = market_analysis.get("volatility", {})
        vol_classification = volatility.get("classification", "MUITO_ALTA")
        
        if vol_classification == "NORMAL":
            score += 6.0
        elif vol_classification == "ALTA":
            score += 4.0
        elif vol_classification == "BAIXA":
            score += 3.0
        else:  # MUITO_ALTA
            score += 1.0
        
        # ═══════════════════════════════════
        # Liquidez
        # ═══════════════════════════════════
        liquidity = market_analysis.get("liquidity", {})
        liquidity_score = liquidity.get("score", 0)
        score += (liquidity_score / 100) * 6.0
        
        # ═══════════════════════════════════
        # Drawdown atual
        # ═══════════════════════════════════
        if risk_analysis:
            current_drawdown = risk_analysis.get("current_drawdown_pct", 0)
            if current_drawdown < 5:
                score += 4.0
            elif current_drawdown < 10:
                score += 2.0
            else:
                score += 0.0
        
        # ═══════════════════════════════════
        # Exposição atual
        # ═══════════════════════════════════
        if risk_analysis:
            exposure = risk_analysis.get("exposure_pct", 0)
            if exposure < 30:
                score += 4.0
            elif exposure < 50:
                score += 2.0
        
        return min(score, max_score)
    
    def _score_context(self, market_analysis: Dict, learning_insights: Dict = None) -> float:
        """
        Avalia contexto temporal e histórico (0-10 pontos).
        """
        score = 0.0
        max_score = 10.0
        
        # ═══════════════════════════════════
        # Sessão de mercado
        # ═══════════════════════════════════
        session = market_analysis.get("session", {})
        if session.get("is_favorable", False):
            score += 4.0
        else:
            score += 1.0
        
        # ═══════════════════════════════════
        # Dia da semana
        # ═══════════════════════════════════
        temporal = market_analysis.get("temporal_context", {})
        day_quality = temporal.get("day_quality", 50)
        
        if day_quality >= 80:
            score += 3.0
        elif day_quality >= 70:
            score += 2.0
        elif day_quality >= 50:
            score += 1.0
        
        # ═══════════════════════════════════
        # Insights de aprendizado
        # ═══════════════════════════════════
        if learning_insights:
            similar_pattern_winrate = learning_insights.get("similar_pattern_winrate", 50)
            if similar_pattern_winrate >= 60:
                score += 3.0
            elif similar_pattern_winrate >= 50:
                score += 1.5
        
        return min(score, max_score)
    
    def _calculate_learning_penalty(self, learning_insights: Dict) -> float:
        """
        Calcula penalização baseada em aprendizado histórico.
        """
        penalty = 0.0
        
        # Se padrão similar já deu prejuízo consistente
        similar_pattern_winrate = learning_insights.get("similar_pattern_winrate", 50)
        
        if similar_pattern_winrate < 40:
            penalty += 15.0
        elif similar_pattern_winrate < 45:
            penalty += 10.0
        
        # Se sequência de losses recente
        recent_losses = learning_insights.get("recent_consecutive_losses", 0)
        if recent_losses >= 3:
            penalty += 10.0
        elif recent_losses >= 2:
            penalty += 5.0
        
        return penalty
    
    def _calculate_risk_reward(self, risk_analysis: Dict) -> float:
        """
        Calcula ratio risco/retorno.
        """
        if not risk_analysis:
            return 1.0
        
        potential_profit = risk_analysis.get("potential_profit", 0)
        potential_loss = risk_analysis.get("potential_loss", 0)
        
        if potential_loss == 0:
            return 0.0
        
        return abs(potential_profit / potential_loss)
    
    def _determine_recommendation(self, score: float, warnings: List[str]) -> str:
        """
        Determina recomendação baseada no score.
        """
        # Warnings críticos bloqueiam execução
        critical_warnings = [w for w in warnings if "Risco/Retorno desfavorável" in w]
        
        if score >= self.THRESHOLD_ALERT and not critical_warnings:
            return "EXECUTE"
        elif score >= self.THRESHOLD_NO_TRADE:
            return "ALERT_ONLY"
        else:
            return "NO_TRADE"
    
    def _calculate_confidence(self, components: Dict, warnings: List[str]) -> float:
        """
        Calcula nível de confiança (0-100).
        """
        # Base: consistência entre componentes
        values = list(components.values())
        expected_values = [25, 20, 25, 20, 10]  # Max de cada componente
        
        normalized = [v / e for v, e in zip(values, expected_values)]
        
        # Desvio padrão (menor = mais consistente)
        std = np.std(normalized)
        consistency_score = max(0, 100 - (std * 100))
        
        # Penalização por warnings
        warning_penalty = len(warnings) * 10
        
        confidence = consistency_score - warning_penalty
        
        return max(0, min(100, confidence))
    
    def get_score_distribution(self) -> Dict:
        """
        Retorna distribuição de scores históricos.
        """
        if not self.score_history:
            return {
                "execute": 0,
                "alert": 0,
                "no_trade": 0,
                "average_score": 0
            }
        
        scores = [s["score"] for s in self.score_history]
        
        return {
            "execute": sum(1 for s in scores if s >= self.THRESHOLD_ALERT),
            "alert": sum(1 for s in scores if self.THRESHOLD_NO_TRADE <= s < self.THRESHOLD_ALERT),
            "no_trade": sum(1 for s in scores if s < self.THRESHOLD_NO_TRADE),
            "average_score": np.mean(scores),
            "total_evaluations": len(scores)
        }
    
    def explain_score(self, score_result: ScoreResult) -> str:
        """
        Gera explicação detalhada do score.
        """
        explanation = []
        
        explanation.append(f"═══════════════════════════════════════")
        explanation.append(f"SCORE TOTAL: {score_result.total_score}/100")
        explanation.append(f"RECOMENDAÇÃO: {score_result.recommendation}")
        explanation.append(f"CONFIANÇA: {score_result.confidence:.1f}%")
        explanation.append(f"═══════════════════════════════════════")
        
        explanation.append(f"\n📊 COMPONENTES:")
        for name, value in score_result.components.items():
            explanation.append(f"  {name.upper():.<20} {value:.1f}")
        
        explanation.append(f"\n✅ RAZÕES:")
        for reason in score_result.reasons:
            explanation.append(f"  • {reason}")
        
        if score_result.warnings:
            explanation.append(f"\n⚠️  AVISOS:")
            for warning in score_result.warnings:
                explanation.append(f"  • {warning}")
        
        explanation.append(f"\n💰 Risco/Retorno: {score_result.risk_reward_ratio:.2f}")
        
        return "\n".join(explanation)


if __name__ == "__main__":
    print("Score Engine - Sistema de Pontuação Profissional")
    print("Módulo pronto para integração")
