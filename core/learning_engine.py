"""
═══════════════════════════════════════════════════════════════════
LEARNING ENGINE - APRENDIZADO E ADAPTAÇÃO AUTOMÁTICA
═══════════════════════════════════════════════════════════════════
Aprende com trades históricos, identifica padrões vencedores/perdedores,
penaliza/reforça automaticamente e ajusta estratégia.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd

from core.memory_engine import MemoryEngine, TradeRecord


class LearningEngine:
    """
    Motor de aprendizado que analisa histórico e ajusta comportamento.
    Identifica padrões consistentes de sucesso/falha e adapta decisões.
    """
    
    def __init__(self, memory: MemoryEngine):
        """
        Inicializa engine de aprendizado.
        
        Args:
            memory: MemoryEngine para acessar histórico de trades
        """
        self.memory = memory
        
        # Cache de insights
        self.pattern_insights = {}
        self.context_insights = {}
        self.temporal_insights = {}
        
        # Última atualização
        self.last_update = None
        
        # Carregar insights iniciais
        self.update_insights()
    
    def update_insights(self):
        """
        Atualiza insights com base no histórico recente.
        """
        print("🧠 Atualizando insights de aprendizado...")
        
        # Insights de padrões
        self.pattern_insights = self._analyze_patterns()
        
        # Insights de contexto
        self.context_insights = self._analyze_context()
        
        # Insights temporais
        self.temporal_insights = self._analyze_temporal()
        
        self.last_update = datetime.now()
        
        print(f"✅ Insights atualizados | Padrões analisados: {len(self.pattern_insights)}")
    
    def get_learning_insights(self, current_context: Dict) -> Dict:
        """
        Retorna insights de aprendizado para contexto atual.
        
        Args:
            current_context: Contexto atual do mercado
        
        Returns:
            Dict com insights relevantes
        """
        insights = {
            "similar_pattern_winrate": self._get_pattern_winrate(
                current_context.get("primary_pattern")
            ),
            
            "context_favorable": self._is_context_favorable(current_context),
            
            "recent_consecutive_losses": self._get_recent_consecutive_losses(),
            
            "hot_streak": self._detect_hot_streak(),
            
            "cold_streak": self._detect_cold_streak(),
            
            "best_time_to_trade": self._get_best_trading_times(),
            
            "avoid_conditions": self._get_conditions_to_avoid(),
            
            "recommended_adjustments": self._get_recommended_adjustments()
        }
        
        return insights
    
    def _analyze_patterns(self) -> Dict:
        """
        Analisa performance de cada padrão.
        """
        pattern_stats = {}
        
        # Obter melhores e piores padrões
        best_patterns = self.memory.get_best_patterns(min_trades=3)
        worst_patterns = self.memory.get_worst_patterns(min_trades=3)
        
        # Marcar padrões vencedores
        for pattern_data in best_patterns[:5]:  # Top 5
            pattern = pattern_data["pattern"]
            pattern_stats[pattern] = {
                "type": "WINNER",
                "winrate": pattern_data["win_rate"],
                "avg_pnl": pattern_data["avg_pnl"],
                "total_trades": pattern_data["total_trades"],
                "score_adjustment": +10  # Bonus
            }
        
        # Marcar padrões perdedores
        for pattern_data in worst_patterns[:5]:  # Bottom 5
            pattern = pattern_data["pattern"]
            if pattern_data["win_rate"] < 45:  # Winrate < 45%
                pattern_stats[pattern] = {
                    "type": "LOSER",
                    "winrate": pattern_data["win_rate"],
                    "avg_pnl": pattern_data["avg_pnl"],
                    "total_trades": pattern_data["total_trades"],
                    "score_adjustment": -15  # Penalty
                }
        
        return pattern_stats
    
    def _analyze_context(self) -> Dict:
        """
        Analisa quais contextos de mercado são favoráveis.
        """
        context_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0.0})
        
        # Buscar trades dos últimos 30 dias
        trades = self.memory.get_all_trades(
            start_date=(datetime.now() - timedelta(days=30)).isoformat()
        )
        
        for trade in trades:
            # Por tendência
            key = f"trend_{trade.market_trend}"
            context_stats[key]["wins"] += 1 if trade.was_win else 0
            context_stats[key]["losses"] += 0 if trade.was_win else 1
            context_stats[key]["total_pnl"] += trade.pnl
            
            # Por volatilidade
            key = f"vol_{trade.volatility_level}"
            context_stats[key]["wins"] += 1 if trade.was_win else 0
            context_stats[key]["losses"] += 0 if trade.was_win else 1
            context_stats[key]["total_pnl"] += trade.pnl
            
            # Por sessão
            key = f"session_{trade.session}"
            context_stats[key]["wins"] += 1 if trade.was_win else 0
            context_stats[key]["losses"] += 0 if trade.was_win else 1
            context_stats[key]["total_pnl"] += trade.pnl
        
        # Calcular winrates
        insights = {}
        for context, stats in context_stats.items():
            total = stats["wins"] + stats["losses"]
            if total >= 3:  # Mínimo de trades
                winrate = (stats["wins"] / total) * 100
                
                insights[context] = {
                    "winrate": round(winrate, 2),
                    "avg_pnl": round(stats["total_pnl"] / total, 2),
                    "favorable": winrate >= 55
                }
        
        return insights
    
    def _analyze_temporal(self) -> Dict:
        """
        Analisa performance por horário/dia da semana.
        """
        temporal_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0.0})
        
        trades = self.memory.get_all_trades(
            start_date=(datetime.now() - timedelta(days=30)).isoformat()
        )
        
        for trade in trades:
            timestamp = datetime.fromisoformat(trade.timestamp)
            
            # Por dia da semana
            weekday = timestamp.strftime("%A")
            key = f"weekday_{weekday}"
            temporal_stats[key]["wins"] += 1 if trade.was_win else 0
            temporal_stats[key]["losses"] += 0 if trade.was_win else 1
            temporal_stats[key]["total_pnl"] += trade.pnl
            
            # Por hora do dia
            hour = timestamp.hour
            key = f"hour_{hour}"
            temporal_stats[key]["wins"] += 1 if trade.was_win else 0
            temporal_stats[key]["losses"] += 0 if trade.was_win else 1
            temporal_stats[key]["total_pnl"] += trade.pnl
        
        # Calcular insights
        insights = {}
        for context, stats in temporal_stats.items():
            total = stats["wins"] + stats["losses"]
            if total >= 2:
                winrate = (stats["wins"] / total) * 100
                
                insights[context] = {
                    "winrate": round(winrate, 2),
                    "avg_pnl": round(stats["total_pnl"] / total, 2),
                    "favorable": winrate >= 55
                }
        
        return insights
    
    def _get_pattern_winrate(self, pattern: Optional[str]) -> float:
        """
        Retorna winrate de um padrão específico.
        """
        if not pattern or pattern not in self.pattern_insights:
            return 50.0  # Neutro
        
        return self.pattern_insights[pattern]["winrate"]
    
    def _is_context_favorable(self, context: Dict) -> bool:
        """
        Verifica se contexto atual é favorável baseado em histórico.
        """
        favorable_count = 0
        total_checks = 0
        
        # Checar tendência
        trend_key = f"trend_{context.get('market_trend', 'NEUTRAL')}"
        if trend_key in self.context_insights:
            favorable_count += 1 if self.context_insights[trend_key]["favorable"] else 0
            total_checks += 1
        
        # Checar volatilidade
        vol_key = f"vol_{context.get('volatility_level', 'NORMAL')}"
        if vol_key in self.context_insights:
            favorable_count += 1 if self.context_insights[vol_key]["favorable"] else 0
            total_checks += 1
        
        # Checar sessão
        session_key = f"session_{context.get('session', 'OFF_HOURS')}"
        if session_key in self.context_insights:
            favorable_count += 1 if self.context_insights[session_key]["favorable"] else 0
            total_checks += 1
        
        if total_checks == 0:
            return True  # Sem dados, assumir favorável
        
        # Favorável se maioria dos checks passar
        return favorable_count >= (total_checks / 2)
    
    def _get_recent_consecutive_losses(self) -> int:
        """
        Conta losses consecutivos recentes.
        """
        trades = self.memory.get_all_trades()
        
        if not trades:
            return 0
        
        # Trades estão em ordem DESC (mais recente primeiro)
        consecutive = 0
        for trade in trades:
            if not trade.was_win:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    def _detect_hot_streak(self) -> bool:
        """
        Detecta sequência de wins (hot streak).
        """
        trades = self.memory.get_all_trades()
        
        if len(trades) < 3:
            return False
        
        # Últimos 3 trades
        recent = trades[:3]
        
        return all(t.was_win for t in recent)
    
    def _detect_cold_streak(self) -> bool:
        """
        Detecta sequência de losses (cold streak).
        """
        trades = self.memory.get_all_trades()
        
        if len(trades) < 3:
            return False
        
        # Últimos 3 trades
        recent = trades[:3]
        
        return all(not t.was_win for t in recent)
    
    def _get_best_trading_times(self) -> List[Dict]:
        """
        Retorna melhores horários para operar.
        """
        best_times = []
        
        for key, stats in self.temporal_insights.items():
            if key.startswith("hour_") and stats["favorable"]:
                hour = int(key.split("_")[1])
                best_times.append({
                    "hour": hour,
                    "winrate": stats["winrate"],
                    "avg_pnl": stats["avg_pnl"]
                })
        
        # Ordenar por winrate
        best_times.sort(key=lambda x: x["winrate"], reverse=True)
        
        return best_times[:5]  # Top 5
    
    def _get_conditions_to_avoid(self) -> List[str]:
        """
        Lista condições que historicamente levam a losses.
        """
        avoid = []
        
        # Padrões ruins
        for pattern, stats in self.pattern_insights.items():
            if stats["type"] == "LOSER":
                avoid.append(f"Padrão {pattern} (Winrate: {stats['winrate']:.1f}%)")
        
        # Contextos ruins
        for context, stats in self.context_insights.items():
            if not stats["favorable"] and stats["winrate"] < 40:
                avoid.append(f"{context.replace('_', ' ').title()} (Winrate: {stats['winrate']:.1f}%)")
        
        return avoid
    
    def _get_recommended_adjustments(self) -> List[str]:
        """
        Recomendações de ajuste baseadas em aprendizado.
        """
        recommendations = []
        
        # Hot streak
        if self._detect_hot_streak():
            recommendations.append("✅ Hot streak detectado - manter estratégia atual")
        
        # Cold streak
        if self._detect_cold_streak():
            recommendations.append("⚠️  Cold streak - reduzir tamanho de posição")
            recommendations.append("⚠️  Cold streak - aumentar threshold de score")
        
        # Padrões perdedores
        losers = [p for p, s in self.pattern_insights.items() if s["type"] == "LOSER"]
        if losers:
            recommendations.append(f"🚫 Evitar padrões: {', '.join(losers)}")
        
        # Melhores horários
        best_times = self._get_best_trading_times()
        if best_times:
            hours = [str(t["hour"]) for t in best_times[:3]]
            recommendations.append(f"⏰ Melhores horários: {', '.join(hours)}h UTC")
        
        return recommendations
    
    def calculate_pattern_penalty(self, pattern: str) -> float:
        """
        Calcula penalização para um padrão específico.
        
        Returns:
            Penalização em pontos (0 = sem penalização)
        """
        if not pattern or pattern not in self.pattern_insights:
            return 0.0
        
        stats = self.pattern_insights[pattern]
        
        if stats["type"] == "LOSER":
            return abs(stats["score_adjustment"])
        
        return 0.0
    
    def calculate_pattern_bonus(self, pattern: str) -> float:
        """
        Calcula bonus para um padrão específico.
        
        Returns:
            Bonus em pontos (0 = sem bonus)
        """
        if not pattern or pattern not in self.pattern_insights:
            return 0.0
        
        stats = self.pattern_insights[pattern]
        
        if stats["type"] == "WINNER":
            return stats["score_adjustment"]
        
        return 0.0
    
    def should_reduce_aggression(self) -> Tuple[bool, str]:
        """
        Verifica se deve reduzir agressividade.
        
        Returns:
            (should_reduce, reason)
        """
        # Cold streak
        if self._detect_cold_streak():
            return True, "Cold streak detectado"
        
        # Losses consecutivos
        consecutive = self._get_recent_consecutive_losses()
        if consecutive >= 2:
            return True, f"{consecutive} losses consecutivos"
        
        # Performance recente ruim
        stats = self.memory.get_statistics(days=7)
        if stats["total_trades"] >= 10 and stats["win_rate"] < 40:
            return True, f"Winrate semanal baixo: {stats['win_rate']:.1f}%"
        
        return False, ""
    
    def should_increase_aggression(self) -> Tuple[bool, str]:
        """
        Verifica se deve aumentar agressividade.
        
        Returns:
            (should_increase, reason)
        """
        # Hot streak
        if self._detect_hot_streak():
            return True, "Hot streak detectado"
        
        # Performance recente excelente
        stats = self.memory.get_statistics(days=7)
        if stats["total_trades"] >= 10 and stats["win_rate"] >= 65:
            return True, f"Winrate semanal alto: {stats['win_rate']:.1f}%"
        
        return False, ""
    
    def get_learning_summary(self) -> str:
        """
        Gera resumo de insights de aprendizado.
        """
        lines = []
        
        lines.append("═══════════════════════════════════════")
        lines.append("🧠 LEARNING ENGINE - RESUMO")
        lines.append("═══════════════════════════════════════")
        
        # Estatísticas gerais
        stats = self.memory.get_statistics(days=30)
        lines.append(f"\n📊 PERFORMANCE (30 dias):")
        lines.append(f"  Total Trades: {stats['total_trades']}")
        lines.append(f"  Winrate: {stats['win_rate']:.1f}%")
        lines.append(f"  P&L Total: ${stats['total_pnl']:.2f}")
        lines.append(f"  Profit Factor: {stats['profit_factor']}")
        
        # Padrões vencedores
        winners = [p for p, s in self.pattern_insights.items() if s["type"] == "WINNER"]
        if winners:
            lines.append(f"\n✅ PADRÕES VENCEDORES:")
            for pattern in winners:
                stats = self.pattern_insights[pattern]
                lines.append(f"  • {pattern}: {stats['winrate']:.1f}% WR, ${stats['avg_pnl']:.2f} avg")
        
        # Padrões perdedores
        losers = [p for p, s in self.pattern_insights.items() if s["type"] == "LOSER"]
        if losers:
            lines.append(f"\n❌ PADRÕES PERDEDORES (EVITAR):")
            for pattern in losers:
                stats = self.pattern_insights[pattern]
                lines.append(f"  • {pattern}: {stats['winrate']:.1f}% WR, ${stats['avg_pnl']:.2f} avg")
        
        # Recomendações
        recommendations = self._get_recommended_adjustments()
        if recommendations:
            lines.append(f"\n💡 RECOMENDAÇÕES:")
            for rec in recommendations:
                lines.append(f"  {rec}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    print("Learning Engine - Aprendizado e Adaptação Automática")
    print("Módulo pronto para integração")
