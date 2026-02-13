"""
═══════════════════════════════════════════════════════════════════
RISK MANAGER - GESTÃO DE RISCO PROFISSIONAL E INVIOLÁVEL
═══════════════════════════════════════════════════════════════════
Proteção de capital como prioridade absoluta.
Limites rígidos, redução automática, pausas e nunca recuperar loss com risco.
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskState(Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    DANGER = "DANGER"
    LOCKED = "LOCKED"


@dataclass
class RiskLimits:
    """Limites de risco configuráveis."""
    max_daily_loss: float = 500.0           # Perda máxima diária ($)
    max_weekly_loss: float = 1500.0         # Perda máxima semanal ($)
    max_monthly_loss: float = 5000.0        # Perda máxima mensal ($)
    
    daily_profit_target: float = 1000.0     # Meta diária ($)
    weekly_profit_target: float = 3000.0    # Meta semanal ($)
    
    max_trades_per_day: int = 10            # Máximo de trades por dia
    max_consecutive_losses: int = 3         # Máximo de losses consecutivos
    
    base_position_size: float = 0.01        # Tamanho base de posição
    max_position_size: float = 0.10         # Tamanho máximo
    min_position_size: float = 0.001        # Tamanho mínimo
    
    max_drawdown_pct: float = 15.0          # Drawdown máximo (%)
    max_exposure_pct: float = 50.0          # Exposição máxima (%)
    
    reduce_size_after_loss: bool = True     # Reduzir tamanho após loss
    reduction_factor: float = 0.5           # Fator de redução (50%)
    
    pause_after_losses: bool = True         # Pausar após sequência de losses
    pause_duration_minutes: int = 60        # Duração da pausa


@dataclass
class RiskMetrics:
    """Métricas de risco atuais."""
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    
    trades_today: int
    consecutive_losses: int
    consecutive_wins: int
    
    current_drawdown_pct: float
    max_drawdown_pct: float
    
    current_exposure_pct: float
    
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    
    risk_state: str
    is_paused: bool
    pause_until: Optional[datetime]


class RiskManager:
    """
    Gestor de risco profissional com limites rígidos e proteção de capital.
    NUNCA permite quebra de regras de risco.
    """
    
    def __init__(self, limits: RiskLimits = None, state_file: str = "risk_state.json"):
        """
        Inicializa gestor de risco.
        
        Args:
            limits: RiskLimits customizados (opcional)
            state_file: Arquivo para persistir estado
        """
        self.limits = limits or RiskLimits()
        self.state_file = state_file
        
        # Estado carregado ou inicializado
        self.state = self._load_state()
        
        # Reset automático se mudou o dia
        self._check_daily_reset()
    
    def can_trade(self, expected_risk: float = None) -> Tuple[bool, str]:
        """
        Verifica se pode operar.
        
        Args:
            expected_risk: Risco esperado da operação ($)
        
        Returns:
            (pode_operar, motivo)
        """
        self._check_daily_reset()
        
        # ═══════════════════════════════════
        # 1. PAUSADO?
        # ═══════════════════════════════════
        if self.state["is_paused"]:
            if self.state["pause_until"]:
                pause_until = datetime.fromisoformat(self.state["pause_until"])
                if datetime.now() < pause_until:
                    remaining = (pause_until - datetime.now()).seconds // 60
                    return False, f"Bot pausado por mais {remaining} minutos"
                else:
                    # Fim da pausa
                    self.state["is_paused"] = False
                    self.state["pause_until"] = None
                    self._save_state()
            else:
                return False, "Bot pausado manualmente"
        
        # ═══════════════════════════════════
        # 2. LOSS DIÁRIO
        # ═══════════════════════════════════
        if self.state["daily_pnl"] <= -self.limits.max_daily_loss:
            return False, f"Limite de loss diário atingido: ${abs(self.state['daily_pnl']):.2f}"
        
        # ═══════════════════════════════════
        # 3. LOSS SEMANAL
        # ═══════════════════════════════════
        if self.state["weekly_pnl"] <= -self.limits.max_weekly_loss:
            return False, f"Limite de loss semanal atingido: ${abs(self.state['weekly_pnl']):.2f}"
        
        # ═══════════════════════════════════
        # 4. LOSS MENSAL
        # ═══════════════════════════════════
        if self.state["monthly_pnl"] <= -self.limits.max_monthly_loss:
            return False, f"Limite de loss mensal atingido: ${abs(self.state['monthly_pnl']):.2f}"
        
        # ═══════════════════════════════════
        # 5. META DIÁRIA ATINGIDA
        # ═══════════════════════════════════
        if self.state["daily_pnl"] >= self.limits.daily_profit_target:
            return False, f"Meta diária atingida: ${self.state['daily_pnl']:.2f}. Preservar lucro."
        
        # ═══════════════════════════════════
        # 6. MÁXIMO DE TRADES DIÁRIOS
        # ═══════════════════════════════════
        if self.state["trades_today"] >= self.limits.max_trades_per_day:
            return False, f"Máximo de trades diários atingido: {self.state['trades_today']}"
        
        # ═══════════════════════════════════
        # 7. LOSSES CONSECUTIVOS
        # ═══════════════════════════════════
        if self.state["consecutive_losses"] >= self.limits.max_consecutive_losses:
            return False, f"Losses consecutivos ({self.state['consecutive_losses']}). Pausa obrigatória."
        
        # ═══════════════════════════════════
        # 8. DRAWDOWN MÁXIMO
        # ═══════════════════════════════════
        if self.state["current_drawdown_pct"] >= self.limits.max_drawdown_pct:
            return False, f"Drawdown máximo atingido: {self.state['current_drawdown_pct']:.2f}%"
        
        # ═══════════════════════════════════
        # 9. EXPOSIÇÃO MÁXIMA
        # ═══════════════════════════════════
        if self.state["current_exposure_pct"] >= self.limits.max_exposure_pct:
            return False, f"Exposição máxima atingida: {self.state['current_exposure_pct']:.2f}%"
        
        # ═══════════════════════════════════
        # 10. RISCO DA OPERAÇÃO
        # ═══════════════════════════════════
        if expected_risk:
            remaining_daily_risk = self.limits.max_daily_loss - abs(self.state["daily_pnl"])
            if expected_risk > remaining_daily_risk:
                return False, f"Risco da operação (${expected_risk:.2f}) excede margem disponível (${remaining_daily_risk:.2f})"
        
        return True, "Liberado para operar"
    
    def calculate_position_size(
        self,
        account_balance: float,
        stop_loss_distance: float,
        current_price: float
    ) -> float:
        """
        Calcula tamanho de posição baseado em risco e estado atual.
        
        Args:
            account_balance: Saldo da conta ($)
            stop_loss_distance: Distância do stop loss (pips ou %)
            current_price: Preço atual
        
        Returns:
            Tamanho de posição ajustado
        """
        # Base size
        position_size = self.limits.base_position_size
        
        # ═══════════════════════════════════
        # REDUÇÃO APÓS LOSS
        # ═══════════════════════════════════
        if self.limits.reduce_size_after_loss and self.state["consecutive_losses"] > 0:
            reduction = self.limits.reduction_factor ** self.state["consecutive_losses"]
            position_size *= reduction
        
        # ═══════════════════════════════════
        # AUMENTO APÓS WINS (CAUTELOSO)
        # ═══════════════════════════════════
        if self.state["consecutive_wins"] >= 3:
            # Aumento moderado (máx 20%)
            position_size *= min(1.2, 1.0 + (self.state["consecutive_wins"] * 0.05))
        
        # ═══════════════════════════════════
        # ESTADO DE RISCO
        # ═══════════════════════════════════
        risk_state = self._calculate_risk_state()
        
        if risk_state == RiskState.CAUTION:
            position_size *= 0.75
        elif risk_state == RiskState.DANGER:
            position_size *= 0.5
        elif risk_state == RiskState.LOCKED:
            position_size = 0.0
        
        # ═══════════════════════════════════
        # LIMITES ABSOLUTOS
        # ═══════════════════════════════════
        position_size = max(self.limits.min_position_size, position_size)
        position_size = min(self.limits.max_position_size, position_size)
        
        return round(position_size, 3)
    
    def record_trade(
        self,
        profit_loss: float,
        was_win: bool,
        trade_details: Dict = None
    ):
        """
        Registra resultado de trade e atualiza métricas.
        
        Args:
            profit_loss: P&L do trade ($)
            was_win: Se foi win ou loss
            trade_details: Detalhes adicionais do trade
        """
        # Atualizar P&L
        self.state["daily_pnl"] += profit_loss
        self.state["weekly_pnl"] += profit_loss
        self.state["monthly_pnl"] += profit_loss
        
        # Atualizar contadores
        self.state["trades_today"] += 1
        self.state["total_trades"] += 1
        
        # Consecutivos
        if was_win:
            self.state["consecutive_wins"] += 1
            self.state["consecutive_losses"] = 0
            self.state["total_wins"] += 1
            self.state["total_profit"] += profit_loss
        else:
            self.state["consecutive_losses"] += 1
            self.state["consecutive_wins"] = 0
            self.state["total_losses"] += 1
            self.state["total_loss"] += abs(profit_loss)
        
        # Atualizar drawdown
        self._update_drawdown()
        
        # Salvar histórico
        self.state["trade_history"].append({
            "timestamp": datetime.now().isoformat(),
            "pnl": profit_loss,
            "was_win": was_win,
            "details": trade_details or {}
        })
        
        # Limitar histórico (últimos 1000 trades)
        if len(self.state["trade_history"]) > 1000:
            self.state["trade_history"] = self.state["trade_history"][-1000:]
        
        # ═══════════════════════════════════
        # PAUSA AUTOMÁTICA
        # ═══════════════════════════════════
        if (self.limits.pause_after_losses and 
            self.state["consecutive_losses"] >= self.limits.max_consecutive_losses):
            self._activate_pause()
        
        self._save_state()
    
    def get_risk_metrics(self) -> RiskMetrics:
        """
        Retorna métricas de risco atuais.
        """
        # Calcular métricas derivadas
        total_trades = self.state["total_trades"]
        
        if total_trades > 0:
            win_rate = (self.state["total_wins"] / total_trades) * 100
            avg_win = self.state["total_profit"] / max(1, self.state["total_wins"])
            avg_loss = self.state["total_loss"] / max(1, self.state["total_losses"])
            
            if self.state["total_loss"] > 0:
                profit_factor = self.state["total_profit"] / self.state["total_loss"]
            else:
                profit_factor = float('inf') if self.state["total_profit"] > 0 else 0.0
        else:
            win_rate = 0.0
            avg_win = 0.0
            avg_loss = 0.0
            profit_factor = 0.0
        
        risk_state = self._calculate_risk_state()
        
        return RiskMetrics(
            daily_pnl=self.state["daily_pnl"],
            weekly_pnl=self.state["weekly_pnl"],
            monthly_pnl=self.state["monthly_pnl"],
            
            trades_today=self.state["trades_today"],
            consecutive_losses=self.state["consecutive_losses"],
            consecutive_wins=self.state["consecutive_wins"],
            
            current_drawdown_pct=self.state["current_drawdown_pct"],
            max_drawdown_pct=self.state["max_drawdown_pct"],
            
            current_exposure_pct=self.state["current_exposure_pct"],
            
            win_rate=win_rate,
            average_win=avg_win,
            average_loss=avg_loss,
            profit_factor=profit_factor,
            
            risk_state=risk_state.value,
            is_paused=self.state["is_paused"],
            pause_until=datetime.fromisoformat(self.state["pause_until"]) if self.state["pause_until"] else None
        )
    
    def _calculate_risk_state(self) -> RiskState:
        """
        Calcula estado de risco atual.
        """
        # Loss em relação aos limites
        daily_loss_pct = abs(self.state["daily_pnl"]) / self.limits.max_daily_loss * 100
        
        if self.state["is_paused"] or self.state["consecutive_losses"] >= self.limits.max_consecutive_losses:
            return RiskState.LOCKED
        
        if daily_loss_pct > 80 or self.state["current_drawdown_pct"] > 12:
            return RiskState.DANGER
        
        if daily_loss_pct > 50 or self.state["consecutive_losses"] >= 2:
            return RiskState.CAUTION
        
        return RiskState.NORMAL
    
    def _update_drawdown(self):
        """
        Atualiza cálculo de drawdown.
        """
        # Peak (maior saldo)
        current_balance = self.state["initial_balance"] + self.state["monthly_pnl"]
        
        if current_balance > self.state["peak_balance"]:
            self.state["peak_balance"] = current_balance
        
        # Drawdown atual
        if self.state["peak_balance"] > 0:
            drawdown = ((self.state["peak_balance"] - current_balance) / 
                       self.state["peak_balance"] * 100)
            self.state["current_drawdown_pct"] = max(0, drawdown)
            
            # Max drawdown
            if self.state["current_drawdown_pct"] > self.state["max_drawdown_pct"]:
                self.state["max_drawdown_pct"] = self.state["current_drawdown_pct"]
    
    def _activate_pause(self):
        """
        Ativa pausa automática.
        """
        self.state["is_paused"] = True
        self.state["pause_until"] = (
            datetime.now() + timedelta(minutes=self.limits.pause_duration_minutes)
        ).isoformat()
        
        self.state["pause_history"].append({
            "timestamp": datetime.now().isoformat(),
            "reason": f"Losses consecutivos: {self.state['consecutive_losses']}",
            "duration_minutes": self.limits.pause_duration_minutes
        })
        
        print(f"⏸️  PAUSA AUTOMÁTICA ATIVADA por {self.limits.pause_duration_minutes} minutos")
    
    def manual_pause(self):
        """Pausa manual."""
        self.state["is_paused"] = True
        self.state["pause_until"] = None
        self._save_state()
    
    def manual_resume(self):
        """Resume manual."""
        self.state["is_paused"] = False
        self.state["pause_until"] = None
        self._save_state()
    
    def _check_daily_reset(self):
        """
        Verifica se precisa fazer reset diário.
        """
        today = date.today().isoformat()
        
        if self.state["last_reset_date"] != today:
            # Reset diário
            self.state["daily_pnl"] = 0.0
            self.state["trades_today"] = 0
            self.state["last_reset_date"] = today
            
            # Reset semanal (domingo)
            if datetime.now().weekday() == 6:  # Sunday
                self.state["weekly_pnl"] = 0.0
                self.state["last_reset_week"] = today
            
            # Reset mensal (dia 1)
            if datetime.now().day == 1:
                self.state["monthly_pnl"] = 0.0
                self.state["last_reset_month"] = today
            
            self._save_state()
    
    def _load_state(self) -> Dict:
        """
        Carrega estado do arquivo ou inicializa novo.
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Estado inicial
        return {
            "initial_balance": 10000.0,
            "peak_balance": 10000.0,
            
            "daily_pnl": 0.0,
            "weekly_pnl": 0.0,
            "monthly_pnl": 0.0,
            
            "trades_today": 0,
            "consecutive_losses": 0,
            "consecutive_wins": 0,
            
            "total_trades": 0,
            "total_wins": 0,
            "total_losses": 0,
            "total_profit": 0.0,
            "total_loss": 0.0,
            
            "current_drawdown_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "current_exposure_pct": 0.0,
            
            "is_paused": False,
            "pause_until": None,
            
            "last_reset_date": date.today().isoformat(),
            "last_reset_week": date.today().isoformat(),
            "last_reset_month": date.today().isoformat(),
            
            "trade_history": [],
            "pause_history": []
        }
    
    def _save_state(self):
        """
        Salva estado no arquivo.
        """
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)


if __name__ == "__main__":
    print("Risk Manager - Gestão de Risco Profissional")
    print("Módulo pronto para integração")
