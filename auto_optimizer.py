"""
Auto-Optimization System
Otimiza automaticamente parâmetros das estratégias
usando técnicas de otimização avançadas
"""
import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
import logging
from scipy.optimize import differential_evolution, minimize
from itertools import product
import pandas as pd

logger = logging.getLogger(__name__)


class ParameterOptimizer:
    """
    Otimiza parâmetros de estratégias usando múltiplas técnicas
    """
    
    def __init__(self):
        self.best_params = {}
        self.optimization_history = []
    
    def grid_search(self,
                    strategy_func: Callable,
                    param_grid: Dict[str, List],
                    data: Dict,
                    metric: str = 'sharpe_ratio') -> Dict:
        """
        Grid Search para otimização de parâmetros
        
        Args:
            strategy_func: Função da estratégia
            param_grid: Dict com listas de valores para cada parâmetro
            data: Dados de mercado
            metric: Métrica para otimizar ('sharpe_ratio', 'profit_factor', etc)
        
        Returns:
            Dict com melhores parâmetros
        """
        logger.info(f"Iniciando Grid Search com {len(param_grid)} parâmetros...")
        
        # Gerar todas as combinações
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(product(*param_values))
        
        best_score = -np.inf
        best_params = None
        results = []
        
        for i, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))
            
            # Executar estratégia com esses parâmetros
            try:
                result = strategy_func(data, **params)
                score = result.get(metric, 0)
                
                results.append({
                    'params': params,
                    'score': score,
                    **result
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Progresso: {i+1}/{len(combinations)} combinações testadas")
                    
            except Exception as e:
                logger.error(f"Erro com params {params}: {e}")
        
        logger.info(f"Grid Search completo. Melhor {metric}: {best_score:.4f}")
        logger.info(f"Melhores parâmetros: {best_params}")
        
        self.best_params = best_params
        self.optimization_history.append({
            'method': 'grid_search',
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results
        })
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results
        }
    
    def random_search(self,
                      strategy_func: Callable,
                      param_bounds: Dict[str, Tuple],
                      data: Dict,
                      n_iterations: int = 100,
                      metric: str = 'sharpe_ratio') -> Dict:
        """
        Random Search para otimização
        
        Args:
            strategy_func: Função da estratégia
            param_bounds: Dict com (min, max) para cada parâmetro
            data: Dados de mercado
            n_iterations: Número de iterações
            metric: Métrica para otimizar
        
        Returns:
            Dict com melhores parâmetros
        """
        logger.info(f"Iniciando Random Search com {n_iterations} iterações...")
        
        best_score = -np.inf
        best_params = None
        results = []
        
        for i in range(n_iterations):
            # Gerar parâmetros aleatórios
            params = {}
            for param_name, (min_val, max_val) in param_bounds.items():
                if isinstance(min_val, int) and isinstance(max_val, int):
                    params[param_name] = np.random.randint(min_val, max_val + 1)
                else:
                    params[param_name] = np.random.uniform(min_val, max_val)
            
            try:
                result = strategy_func(data, **params)
                score = result.get(metric, 0)
                
                results.append({
                    'params': params,
                    'score': score,
                    **result
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    logger.info(f"Nova melhor score: {best_score:.4f} com params: {best_params}")
                
            except Exception as e:
                logger.error(f"Erro com params {params}: {e}")
        
        logger.info(f"Random Search completo. Melhor {metric}: {best_score:.4f}")
        
        self.best_params = best_params
        self.optimization_history.append({
            'method': 'random_search',
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results
        })
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results
        }
    
    def bayesian_optimization(self,
                             strategy_func: Callable,
                             param_bounds: Dict[str, Tuple],
                             data: Dict,
                             n_iterations: int = 50,
                             metric: str = 'sharpe_ratio') -> Dict:
        """
        Bayesian Optimization usando Differential Evolution
        
        Args:
            strategy_func: Função da estratégia
            param_bounds: Dict com (min, max) para cada parâmetro
            data: Dados de mercado
            n_iterations: Número de iterações
            metric: Métrica para otimizar
        
        Returns:
            Dict com melhores parâmetros
        """
        logger.info(f"Iniciando Bayesian Optimization...")
        
        param_names = list(param_bounds.keys())
        bounds = [param_bounds[name] for name in param_names]
        
        def objective(x):
            params = dict(zip(param_names, x))
            
            # Arredondar inteiros
            for name, (min_val, max_val) in param_bounds.items():
                if isinstance(min_val, int) and isinstance(max_val, int):
                    params[name] = int(round(params[name]))
            
            try:
                result = strategy_func(data, **params)
                score = result.get(metric, 0)
                return -score  # Negative porque differential_evolution minimiza
            except Exception as e:
                logger.error(f"Erro com params {params}: {e}")
                return 1e10  # Valor alto para penalizar
        
        # Executar otimização
        result = differential_evolution(
            objective,
            bounds,
            maxiter=n_iterations,
            popsize=15,
            seed=42,
            workers=1
        )
        
        best_params = dict(zip(param_names, result.x))
        
        # Arredondar inteiros
        for name, (min_val, max_val) in param_bounds.items():
            if isinstance(min_val, int) and isinstance(max_val, int):
                best_params[name] = int(round(best_params[name]))
        
        best_score = -result.fun
        
        logger.info(f"Bayesian Optimization completo. Melhor {metric}: {best_score:.4f}")
        logger.info(f"Melhores parâmetros: {best_params}")
        
        self.best_params = best_params
        self.optimization_history.append({
            'method': 'bayesian',
            'best_params': best_params,
            'best_score': best_score
        })
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'iterations': result.nit,
            'function_evaluations': result.nfev
        }
    
    def walk_forward_optimization(self,
                                  strategy_func: Callable,
                                  param_bounds: Dict[str, Tuple],
                                  data: Dict,
                                  train_size: int = 1000,
                                  test_size: int = 200,
                                  metric: str = 'sharpe_ratio') -> Dict:
        """
        Walk-Forward Optimization
        Otimiza em janela de treinamento, testa em janela de teste
        
        Returns:
            Dict com resultados de cada janela
        """
        logger.info("Iniciando Walk-Forward Optimization...")
        
        prices = data['close']
        n_total = len(prices)
        
        results = []
        current_start = 0
        
        while current_start + train_size + test_size <= n_total:
            train_end = current_start + train_size
            test_end = train_end + test_size
            
            # Dados de treino
            train_data = {
                key: val[current_start:train_end] 
                for key, val in data.items()
            }
            
            # Otimizar na janela de treino
            logger.info(f"Janela {len(results)+1}: Treino [{current_start}:{train_end}]")
            opt_result = self.bayesian_optimization(
                strategy_func, 
                param_bounds, 
                train_data, 
                n_iterations=20,
                metric=metric
            )
            
            # Testar na janela de teste
            test_data = {
                key: val[train_end:test_end] 
                for key, val in data.items()
            }
            
            test_result = strategy_func(test_data, **opt_result['best_params'])
            
            results.append({
                'train_period': (current_start, train_end),
                'test_period': (train_end, test_end),
                'best_params': opt_result['best_params'],
                'train_score': opt_result['best_score'],
                'test_score': test_result.get(metric, 0),
                'test_metrics': test_result
            })
            
            logger.info(
                f"Train {metric}: {opt_result['best_score']:.4f}, "
                f"Test {metric}: {test_result.get(metric, 0):.4f}"
            )
            
            # Mover janela
            current_start += test_size
        
        # Calcular estatísticas
        train_scores = [r['train_score'] for r in results]
        test_scores = [r['test_score'] for r in results]
        
        summary = {
            'n_windows': len(results),
            'avg_train_score': np.mean(train_scores),
            'avg_test_score': np.mean(test_scores),
            'std_test_score': np.std(test_scores),
            'min_test_score': np.min(test_scores),
            'max_test_score': np.max(test_scores),
            'results': results
        }
        
        logger.info(
            f"Walk-Forward completo: {len(results)} janelas, "
            f"Avg test {metric}: {summary['avg_test_score']:.4f} "
            f"(±{summary['std_test_score']:.4f})"
        )
        
        return summary


class AdaptiveLearning:
    """
    Sistema de aprendizado adaptativo
    Ajusta parâmetros automaticamente baseado em performance
    """
    
    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.performance_history = []
        self.param_adjustments = []
    
    def update_params(self,
                      current_params: Dict,
                      performance: float,
                      target_performance: float = 0.6) -> Dict:
        """
        Atualiza parâmetros baseado em performance
        
        Args:
            current_params: Parâmetros atuais
            performance: Performance recente (0-1)
            target_performance: Performance alvo
        
        Returns:
            Dict com parâmetros ajustados
        """
        self.performance_history.append(performance)
        
        # Se performance está abaixo do target, ajustar
        if performance < target_performance:
            adjustment_factor = 1 + (self.learning_rate * (target_performance - performance))
            
            new_params = {}
            for key, value in current_params.items():
                if isinstance(value, (int, float)):
                    # Ajustar valor
                    new_value = value * adjustment_factor
                    
                    # Manter dentro de limites razoáveis
                    if isinstance(value, int):
                        new_params[key] = int(round(new_value))
                    else:
                        new_params[key] = new_value
                else:
                    new_params[key] = value
            
            self.param_adjustments.append({
                'old_params': current_params,
                'new_params': new_params,
                'performance': performance,
                'adjustment_factor': adjustment_factor
            })
            
            logger.info(
                f"Parâmetros ajustados. Performance: {performance:.3f} -> "
                f"Target: {target_performance:.3f}"
            )
            
            return new_params
        
        return current_params
    
    def get_adaptive_threshold(self,
                              recent_volatility: float,
                              base_threshold: float = 0.01) -> float:
        """
        Calcula threshold adaptativo baseado em volatilidade
        
        Returns:
            Threshold ajustado
        """
        # Aumentar threshold em alta volatilidade
        volatility_multiplier = 1 + (recent_volatility * 10)
        adaptive_threshold = base_threshold * volatility_multiplier
        
        return min(adaptive_threshold, base_threshold * 3)  # Max 3x


def create_optimizer() -> ParameterOptimizer:
    """Factory function para criar otimizador"""
    return ParameterOptimizer()


def create_adaptive_learner(learning_rate: float = 0.1) -> AdaptiveLearning:
    """Factory function para criar adaptive learner"""
    return AdaptiveLearning(learning_rate)
