"""
Advanced Backtesting Engine
Sistema completo de backtesting com análise detalhada
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Representa um trade individual"""
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    side: str  # 'long' or 'short'
    size: float
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    duration: Optional[float] = None
    status: str = 'open'  # 'open', 'closed', 'stopped'


class AdvancedBacktest:
    """
    Engine de backtesting avançado
    """
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades = []
        self.equity_curve = []
        self.positions = []
        
    def run(self,
            data: Dict[str, np.ndarray],
            strategy_func: callable,
            **strategy_params) -> Dict:
        """
        Executa backtest
        
        Args:
            data: Dict com OHLCV
            strategy_func: Função que retorna sinais
            **strategy_params: Parâmetros da estratégia
        
        Returns:
            Dict com métricas de performance
        """
        logger.info(f"Iniciando backtest com capital inicial: ${self.initial_capital:,.2f}")
        
        prices = data['close']
        n_periods = len(prices)
        
        self.current_capital = self.initial_capital
        self.equity_curve = [self.initial_capital]
        self.trades = []
        current_position = None
        
        for i in range(1, n_periods):
            # Dados até o período atual (sem look-ahead bias)
            current_data = {
                key: val[:i+1] for key, val in data.items()
            }
            
            # Gerar sinal
            try:
                signal = strategy_func(current_data, **strategy_params)
                signal_type = signal.get('signal', 'NEUTRAL')
            except:
                signal_type = 'NEUTRAL'
            
            current_price = prices[i]
            
            # Executar trade baseado no sinal
            if current_position is None:
                # Sem posição, procurar entrada
                if signal_type == 'BUY':
                    # Calcular tamanho da posição (1% do capital)
                    position_size = (self.current_capital * 0.01) / current_price
                    
                    current_position = Trade(
                        entry_time=i,
                        exit_time=None,
                        entry_price=current_price,
                        exit_price=None,
                        side='long',
                        size=position_size,
                        status='open'
                    )
                    
                elif signal_type == 'SELL':
                    position_size = (self.current_capital * 0.01) / current_price
                    
                    current_position = Trade(
                        entry_time=i,
                        exit_time=None,
                        entry_price=current_price,
                        exit_price=None,
                        side='short',
                        size=position_size,
                        status='open'
                    )
            
            else:
                # Com posição, verificar saída
                exit_signal = False
                
                # Sinal oposto
                if (current_position.side == 'long' and signal_type == 'SELL') or \
                   (current_position.side == 'short' and signal_type == 'BUY'):
                    exit_signal = True
                
                # Stop loss (2%)
                if current_position.side == 'long':
                    if current_price < current_position.entry_price * 0.98:
                        exit_signal = True
                        current_position.status = 'stopped'
                else:  # short
                    if current_price > current_position.entry_price * 1.02:
                        exit_signal = True
                        current_position.status = 'stopped'
                
                # Take profit (4%)
                if current_position.side == 'long':
                    if current_price > current_position.entry_price * 1.04:
                        exit_signal = True
                else:  # short
                    if current_price < current_position.entry_price * 0.96:
                        exit_signal = True
                
                if exit_signal:
                    # Fechar posição
                    current_position.exit_time = i
                    current_position.exit_price = current_price
                    current_position.duration = i - current_position.entry_time
                    
                    # Calcular P&L
                    if current_position.side == 'long':
                        pnl = (current_price - current_position.entry_price) * current_position.size
                    else:  # short
                        pnl = (current_position.entry_price - current_price) * current_position.size
                    
                    current_position.pnl = pnl
                    current_position.pnl_pct = (pnl / (current_position.entry_price * current_position.size)) * 100
                    
                    if current_position.status != 'stopped':
                        current_position.status = 'closed'
                    
                    self.current_capital += pnl
                    self.trades.append(current_position)
                    current_position = None
            
            # Calcular equity
            equity = self.current_capital
            if current_position:
                # Incluir P&L não realizado
                if current_position.side == 'long':
                    unrealized_pnl = (current_price - current_position.entry_price) * current_position.size
                else:
                    unrealized_pnl = (current_position.entry_price - current_price) * current_position.size
                equity += unrealized_pnl
            
            self.equity_curve.append(equity)
        
        # Fechar posição final se ainda aberta
        if current_position:
            current_position.exit_time = n_periods - 1
            current_position.exit_price = prices[-1]
            current_position.duration = n_periods - 1 - current_position.entry_time
            
            if current_position.side == 'long':
                pnl = (prices[-1] - current_position.entry_price) * current_position.size
            else:
                pnl = (current_position.entry_price - prices[-1]) * current_position.size
            
            current_position.pnl = pnl
            current_position.pnl_pct = (pnl / (current_position.entry_price * current_position.size)) * 100
            current_position.status = 'closed'
            
            self.current_capital += pnl
            self.trades.append(current_position)
        
        # Calcular métricas
        metrics = self._calculate_metrics()
        
        logger.info(f"Backtest completo: {len(self.trades)} trades")
        logger.info(f"Capital final: ${self.current_capital:,.2f}")
        logger.info(f"Retorno total: {metrics['total_return']:.2f}%")
        logger.info(f"Win rate: {metrics['win_rate']:.2f}%")
        logger.info(f"Sharpe ratio: {metrics['sharpe_ratio']:.3f}")
        
        return metrics
    
    def _calculate_metrics(self) -> Dict:
        """Calcula métricas de performance"""
        if not self.trades:
            return {
                'total_return': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        
        # Basic metrics
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        total_return = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        win_rate = (len(winning_trades) / len(self.trades)) * 100 if self.trades else 0
        
        # Profit factor
        total_wins = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Sharpe ratio
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if len(returns) > 0 and np.std(returns) > 0 else 0
        
        # Max drawdown
        equity_arr = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_arr)
        drawdown = (equity_arr - running_max) / running_max
        max_drawdown = np.min(drawdown) * 100
        
        # Average trade metrics
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t.pnl) for t in losing_trades]) if losing_trades else 0
        avg_trade_duration = np.mean([t.duration for t in self.trades])
        
        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_trade_duration': avg_trade_duration,
            'final_capital': self.current_capital
        }
    
    def get_trade_history(self) -> pd.DataFrame:
        """Retorna histórico de trades como DataFrame"""
        if not self.trades:
            return pd.DataFrame()
        
        return pd.DataFrame([
            {
                'entry_time': t.entry_time,
                'exit_time': t.exit_time,
                'entry_price': t.entry_price,
                'exit_price': t.exit_price,
                'side': t.side,
                'size': t.size,
                'pnl': t.pnl,
                'pnl_pct': t.pnl_pct,
                'duration': t.duration,
                'status': t.status
            }
            for t in self.trades
        ])
    
    def monte_carlo_simulation(self, n_simulations: int = 1000) -> Dict:
        """
        Simulação Monte Carlo para estimar distribuição de resultados
        
        Returns:
            Dict com estatísticas das simulações
        """
        if not self.trades:
            return {}
        
        logger.info(f"Executando {n_simulations} simulações Monte Carlo...")
        
        # Extrair P&L dos trades
        trade_pnls = [t.pnl for t in self.trades]
        
        simulation_results = []
        
        for _ in range(n_simulations):
            # Randomizar ordem dos trades
            shuffled_pnls = np.random.choice(trade_pnls, size=len(trade_pnls), replace=True)
            
            # Calcular equity curve
            simulated_equity = self.initial_capital + np.cumsum(shuffled_pnls)
            final_capital = simulated_equity[-1]
            
            # Calcular drawdown
            running_max = np.maximum.accumulate(simulated_equity)
            drawdown = (simulated_equity - running_max) / running_max
            max_drawdown = np.min(drawdown) * 100
            
            simulation_results.append({
                'final_capital': final_capital,
                'return': ((final_capital - self.initial_capital) / self.initial_capital) * 100,
                'max_drawdown': max_drawdown
            })
        
        # Estatísticas
        returns = [r['return'] for r in simulation_results]
        drawdowns = [r['max_drawdown'] for r in simulation_results]
        
        stats = {
            'mean_return': np.mean(returns),
            'median_return': np.median(returns),
            'std_return': np.std(returns),
            'min_return': np.min(returns),
            'max_return': np.max(returns),
            'percentile_5': np.percentile(returns, 5),
            'percentile_95': np.percentile(returns, 95),
            'mean_drawdown': np.mean(drawdowns),
            'worst_drawdown': np.min(drawdowns),
            'probability_profit': (np.array(returns) > 0).mean() * 100,
            'simulations': simulation_results
        }
        
        logger.info(
            f"Monte Carlo: Retorno médio: {stats['mean_return']:.2f}% "
            f"(±{stats['std_return']:.2f}%), "
            f"Prob lucro: {stats['probability_profit']:.1f}%"
        )
        
        return stats


class RiskAnalyzer:
    """
    Análise avançada de risco
    """
    
    @staticmethod
    def calculate_var(returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Value at Risk (VaR)
        
        Returns:
            VaR no nível de confiança especificado
        """
        return np.percentile(returns, (1 - confidence) * 100)
    
    @staticmethod
    def calculate_cvar(returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Conditional Value at Risk (CVaR) / Expected Shortfall
        
        Returns:
            CVaR no nível de confiança especificado
        """
        var = RiskAnalyzer.calculate_var(returns, confidence)
        return np.mean(returns[returns <= var])
    
    @staticmethod
    def calculate_sortino_ratio(returns: np.ndarray, target_return: float = 0) -> float:
        """
        Sortino Ratio (foca apenas em downside risk)
        
        Returns:
            Sortino ratio
        """
        excess_returns = returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        
        if downside_std == 0:
            return 0
        
        return np.mean(excess_returns) / downside_std * np.sqrt(252)
    
    @staticmethod
    def calculate_calmar_ratio(returns: np.ndarray, equity_curve: np.ndarray) -> float:
        """
        Calmar Ratio (retorno anualizado / max drawdown)
        
        Returns:
            Calmar ratio
        """
        annual_return = np.mean(returns) * 252
        
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - running_max) / running_max
        max_drawdown = abs(np.min(drawdown))
        
        if max_drawdown == 0:
            return 0
        
        return annual_return / max_drawdown


def create_backtest(initial_capital: float = 10000) -> AdvancedBacktest:
    """Factory function para criar backtest"""
    return AdvancedBacktest(initial_capital)
