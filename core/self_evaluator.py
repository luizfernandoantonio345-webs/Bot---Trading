"""
═══════════════════════════════════════════════════════════════════
CAMADA 10: META-INTELIGÊNCIA & AUTO-AVALIAÇÃO
═══════════════════════════════════════════════════════════════════
O bot avalia a si mesmo diariamente e ajusta autonomamente.
"""

import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import numpy as np
from core.logger import get_logger


@dataclass
class DailyPerformance:
    """Performance diária do bot"""
    date: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    expectancy: float  # EV (expected value)
    max_drawdown: float
    sharpe_ratio: float
    entry_quality: float  # 0-100
    risk_adjusted_return: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class SelfEvaluator:
    """
    Sistema de autoavaliação contínua.
    Avalia performance e ajusta pesos/frequência/agressividade.
    """
    
    def __init__(self, memory_engine=None):
        self.logger = get_logger()
        self.memory = memory_engine
        self.state_file = "data/self_evaluation_state.json"
        self.performance_history: List[DailyPerformance] = []
        self.adjustment_history: List[Dict] = []
        
        # Limites de performance
        self.min_acceptable_winrate = 0.50
        self.min_acceptable_ev = 0.1
        self.max_acceptable_drawdown = 0.15
        
        # Pesos ajustáveis
        self.current_weights = {
            "trend": 0.25,
            "momentum": 0.20,
            "confirmations": 0.25,
            "risk_quality": 0.20,
            "context": 0.10
        }
        
        # Frequência de operação
        self.base_trades_per_day = 10
        self.current_frequency_factor = 1.0
        
        # Agressividade
        self.base_position_size = 0.01
        self.current_aggressiveness = 1.0
        
        self._load_state()
    
    def evaluate_daily_performance(self) -> DailyPerformance:
        """
        Avalia performance do dia completo.
        """
        if not self.memory:
            return None
        
        # Obter trades de hoje
        today = datetime.now().strftime("%Y-%m-%d")
        stats = self.memory.get_statistics(days=1)
        
        trades = self.memory.get_trades_for_date(today)
        if not trades:
            return None
        
        # Cálculos
        total = len(trades)
        winners = sum(1 for t in trades if t.pnl > 0)
        losers = sum(1 for t in trades if t.pnl < 0)
        win_rate = winners / total if total > 0 else 0
        
        # Expectancy (EV)
        total_pnl = sum(t.pnl for t in trades)
        expectancy = total_pnl / total if total > 0 else 0
        
        # Drawdown
        cumulative_pnl = 0
        max_drawdown = 0
        peak = 0
        for trade in trades:
            cumulative_pnl += trade.pnl
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            else:
                dd = (peak - cumulative_pnl) / peak if peak > 0 else 0
                max_drawdown = max(max_drawdown, dd)
        
        # Qualidade de entradas (baseado em risk/reward)
        entry_qualities = []
        for trade in trades:
            if trade.risk > 0:
                rr = trade.pnl / trade.risk if trade.pnl != 0 else 0
                eq = min(100, max(0, (rr + 1) * 25))  # Scale 0-100
                entry_qualities.append(eq)
        entry_quality = np.mean(entry_qualities) if entry_qualities else 0
        
        # Sharpe Ratio
        returns = [t.pnl for t in trades]
        if len(returns) > 1:
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        # Risk-adjusted return
        risk_adjusted = (total_pnl / max(abs(sum(t.risk for t in trades)), 1)) * 100
        
        # Criar objeto de performance
        perf = DailyPerformance(
            date=today,
            total_trades=total,
            winning_trades=winners,
            losing_trades=losers,
            win_rate=win_rate,
            expectancy=expectancy,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            entry_quality=entry_quality,
            risk_adjusted_return=risk_adjusted
        )
        
        self.performance_history.append(perf)
        self._log_evaluation(perf)
        
        return perf
    
    def adjust_weights_based_on_performance(self) -> Dict:
        """
        Ajusta pesos do score baseado na performance histórica.
        """
        if len(self.performance_history) < 5:
            return None  # Precisa de mais dados
        
        recent_perf = self.performance_history[-5:]
        
        adjustments = {}
        
        # Se win rate baixo, aumentar peso em confirmações
        avg_winrate = np.mean([p.win_rate for p in recent_perf])
        if avg_winrate < self.min_acceptable_winrate:
            adjustments["confirmations"] = self.current_weights["confirmations"] * 1.15
            adjustments["trend"] = self.current_weights["trend"] * 0.90
            self.logger.log_system_event(
                "WEIGHT_ADJUSTMENT",
                f"Win rate baixo ({avg_winrate:.1%}). Aumentando peso em confirmações."
            )
        
        # Se expectancy baixa, aumentar peso em risk_quality
        avg_ev = np.mean([p.expectancy for p in recent_perf])
        if avg_ev < self.min_acceptable_ev:
            adjustments["risk_quality"] = self.current_weights["risk_quality"] * 1.20
            adjustments["momentum"] = self.current_weights["momentum"] * 0.85
            self.logger.log_system_event(
                "WEIGHT_ADJUSTMENT",
                f"EV baixo ({avg_ev:.2f}). Aumentando peso em qualidade de risco."
            )
        
        # Se drawdown muito alto, aumentar peso em contexto
        avg_dd = np.mean([p.max_drawdown for p in recent_perf])
        if avg_dd > self.max_acceptable_drawdown:
            adjustments["context"] = self.current_weights["context"] * 1.25
            adjustments["momentum"] = self.current_weights["momentum"] * 0.80
            self.logger.log_system_event(
                "WEIGHT_ADJUSTMENT",
                f"Drawdown muito alto ({avg_dd:.1%}). Aumentando peso em contexto."
            )
        
        # Normalizar e aplicar
        if adjustments:
            # Adicionar pesos não ajustados
            for key in self.current_weights:
                if key not in adjustments:
                    adjustments[key] = self.current_weights[key]
            
            # Normalizar
            total_weight = sum(adjustments.values())
            adjustments = {k: v/total_weight for k, v in adjustments.items()}
            
            self.current_weights = adjustments
            self.adjustment_history.append({
                "timestamp": datetime.now().isoformat(),
                "weights": adjustments.copy(),
                "reason": "Performance-based adjustment"
            })
            
            return adjustments
        
        return None
    
    def adjust_frequency_based_on_performance(self) -> float:
        """
        Ajusta frequência de trades baseado na performance.
        """
        if len(self.performance_history) < 3:
            return self.current_frequency_factor
        
        recent_perf = self.performance_history[-3:]
        
        # Se performance excelente, aumentar frequência
        avg_winrate = np.mean([p.win_rate for p in recent_perf])
        avg_ev = np.mean([p.expectancy for p in recent_perf])
        
        if avg_winrate > 0.60 and avg_ev > 0.5:
            new_factor = min(1.5, self.current_frequency_factor * 1.10)
            self.logger.log_system_event(
                "FREQUENCY_INCREASE",
                f"Performance excelente. Aumentando frequência para {new_factor:.2f}x"
            )
        
        # Se performance ruim, diminuir frequência
        elif avg_winrate < 0.45 or avg_ev < 0.0:
            new_factor = max(0.5, self.current_frequency_factor * 0.85)
            self.logger.log_system_event(
                "FREQUENCY_DECREASE",
                f"Performance ruim. Diminuindo frequência para {new_factor:.2f}x"
            )
        else:
            return self.current_frequency_factor
        
        self.current_frequency_factor = new_factor
        return new_factor
    
    def adjust_aggressiveness(self) -> float:
        """
        Ajusta agressividade (tamanho de posição) baseado em drawdown.
        """
        if len(self.performance_history) < 2:
            return self.current_aggressiveness
        
        recent_perf = self.performance_history[-1]
        
        # Se drawdown muito alto, reduzir agressividade
        if recent_perf.max_drawdown > self.max_acceptable_drawdown:
            new_agg = max(0.3, self.current_aggressiveness * 0.80)
            self.logger.log_system_event(
                "AGGRESSIVENESS_REDUCED",
                f"Drawdown muito alto ({recent_perf.max_drawdown:.1%}). "
                f"Reduzindo tamanho de posição para {new_agg:.2f}x"
            )
            self.current_aggressiveness = new_agg
        
        # Se drawdown voltou ao normal, recuperar agressividade gradualmente
        elif recent_perf.max_drawdown < 0.08 and self.current_aggressiveness < 1.0:
            new_agg = min(1.0, self.current_aggressiveness * 1.05)
            self.logger.log_system_event(
                "AGGRESSIVENESS_RECOVERY",
                f"Drawdown normalizado. Aumentando agressividade para {new_agg:.2f}x"
            )
            self.current_aggressiveness = new_agg
        
        return self.current_aggressiveness
    
    def get_evaluation_summary(self) -> Dict:
        """
        Retorna resumo da autoavaliação.
        """
        if not self.performance_history:
            return None
        
        recent = self.performance_history[-7:]  # Última semana
        
        return {
            "period": "Last 7 days",
            "avg_winrate": np.mean([p.win_rate for p in recent]),
            "avg_expectancy": np.mean([p.expectancy for p in recent]),
            "avg_drawdown": np.mean([p.max_drawdown for p in recent]),
            "total_trades": sum(p.total_trades for p in recent),
            "current_weights": self.current_weights,
            "frequency_factor": self.current_frequency_factor,
            "aggressiveness": self.current_aggressiveness,
            "performance_trend": self._calculate_trend(recent)
        }
    
    def _calculate_trend(self, perfs: List[DailyPerformance]) -> str:
        """Calcula tendência de performance"""
        if len(perfs) < 2:
            return "INSUFFICIENT_DATA"
        
        recent_wr = perfs[-1].win_rate
        previous_wr = np.mean([p.win_rate for p in perfs[:-1]])
        
        if recent_wr > previous_wr * 1.10:
            return "IMPROVING"
        elif recent_wr < previous_wr * 0.90:
            return "DETERIORATING"
        else:
            return "STABLE"
    
    def _log_evaluation(self, perf: DailyPerformance):
        """Log detalhado da avaliação"""
        self.logger.log_decision(
            score=perf.entry_quality,
            recommendation=f"PERF_WR_{perf.win_rate:.1%}_EV_{perf.expectancy:.2f}",
            reasons=[
                f"Trades: {perf.total_trades} ({perf.winning_trades}W/{perf.losing_trades}L)",
                f"Expectancy: {perf.expectancy:.2f}",
                f"Drawdown: {perf.max_drawdown:.1%}",
                f"Sharpe: {perf.sharpe_ratio:.2f}",
                f"Entry Quality: {perf.entry_quality:.1f}"
            ],
            warnings=[
                f"Low WR" if perf.win_rate < 0.50 else "",
                f"Negative EV" if perf.expectancy < 0 else "",
                f"High DD" if perf.max_drawdown > 0.15 else ""
            ]
        )
    
    def _load_state(self):
        """Carrega estado persistente"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.current_weights = data.get("weights", self.current_weights)
                    self.current_frequency_factor = data.get("frequency_factor", 1.0)
                    self.current_aggressiveness = data.get("aggressiveness", 1.0)
            except:
                pass
    
    def save_state(self):
        """Salva estado persistente"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump({
                "weights": self.current_weights,
                "frequency_factor": self.current_frequency_factor,
                "aggressiveness": self.current_aggressiveness,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
