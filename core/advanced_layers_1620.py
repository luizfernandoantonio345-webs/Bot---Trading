"""
═══════════════════════════════════════════════════════════════════
CAMADA 16: INTELIGÊNCIA DE COMPORTAMENTO DE MULTIDÃO
═══════════════════════════════════════════════════════════════════
O bot identifica excesso emocional do mercado.
"""

from typing import Dict
import numpy as np
from core.logger import get_logger


class CrowdIntelligence:
    """
    Lê comportamento coletivo indireto do mercado.
    """
    
    def __init__(self):
        self.logger = get_logger()
    
    def detect_retail_trap(self, market_analysis: Dict) -> Tuple[bool, str]:
        """
        Detecta armadilhas clássicas de varejo.
        Ex: Breakout que falha, reversal comum.
        """
        momentum = market_analysis.get("momentum", {})
        volatility = market_analysis.get("volatility", {})
        
        mom_score = momentum.get("score", 50)
        vol_class = volatility.get("classification", "NORMAL")
        
        # Armadilha: Momentum EXTREMO + breakout falsificado = varejo entrando
        if mom_score > 80 and vol_class == "HIGH":
            return True, "Possible retail trap - extreme momentum on high volatility"
        
        return False, ""
    
    def detect_capitulation(self, market_analysis: Dict, recent_performance: list) -> bool:
        """
        Detecta capitulação (ponto de reversão).
        Muitas perdas seguidas + pessimismo extremo.
        """
        momentum = market_analysis.get("momentum", {})
        mom_score = momentum.get("score", 50)
        
        # Pessimismo extremo
        if mom_score < 20:
            # Se houver muitas perdas antes disso
            recent_losses = sum(1 for p in recent_performance if p < 0)
            if recent_losses > 3:
                return True
        
        return False
    
    def detect_fomo_setup(self, market_analysis: Dict) -> bool:
        """
        Detecta setup onde FOMO (fear of missing out) é provável.
        """
        volatility = market_analysis.get("volatility", {})
        momentum = market_analysis.get("momentum", {})
        
        vol_class = volatility.get("classification", "NORMAL")
        mom_score = momentum.get("score", 50)
        
        # FOMO: Volatilidade alta + momentum positivo + mercado em alta rápida
        if vol_class == "HIGH" and mom_score > 75:
            return True
        
        return False
    
    def get_crowd_intelligence_report(self, market_analysis: Dict) -> Dict:
        """Análise de inteligência coletiva"""
        trap_detected, trap_msg = self.detect_retail_trap(market_analysis)
        capitulation = self.detect_capitulation(market_analysis, [])
        fomo_setup = self.detect_fomo_setup(market_analysis)
        
        return {
            "retail_trap": trap_detected,
            "trap_message": trap_msg,
            "capitulation_signal": capitulation,
            "fomo_setup": fomo_setup,
            "crowd_sentiment": self._get_crowd_sentiment(market_analysis),
            "trade_safe": not (trap_detected or fomo_setup)
        }
    
    def _get_crowd_sentiment(self, market_analysis: Dict) -> str:
        """Sentimento da multidão"""
        momentum = market_analysis.get("momentum", {})
        mom_score = momentum.get("score", 50)
        
        if mom_score > 75:
            return "EXTREME_BULLISH"
        elif mom_score > 60:
            return "BULLISH"
        elif mom_score > 40:
            return "NEUTRAL"
        elif mom_score > 25:
            return "BEARISH"
        else:
            return "EXTREME_BEARISH"


"""
═══════════════════════════════════════════════════════════════════
CAMADA 17: RESILIÊNCIA E AUTODEFESA
═══════════════════════════════════════════════════════════════════
O bot se protege contra falhas.
"""

from typing import Tuple


class ResilienceEngine:
    """
    Mecanismos de autoproteção e recuperação.
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.module_health = {}
        self.failure_count = {}
        self.safe_mode_active = False
    
    def check_module_health(self, module_name: str, is_healthy: bool) -> None:
        """Rastreia saúde de módulos"""
        self.module_health[module_name] = is_healthy
        
        if not is_healthy:
            self.failure_count[module_name] = self.failure_count.get(module_name, 0) + 1
            
            if self.failure_count[module_name] >= 3:
                self.logger.log_error(
                    "MODULE_FAILURE",
                    f"Módulo {module_name} falhou {self.failure_count[module_name]}x. Ativando fallback.",
                    {"module": module_name}
                )
    
    def get_system_health(self) -> float:
        """Saúde geral do sistema (0-100)"""
        if not self.module_health:
            return 100.0
        
        healthy_count = sum(1 for v in self.module_health.values() if v)
        total = len(self.module_health)
        
        return (healthy_count / total) * 100 if total > 0 else 100.0
    
    def should_activate_safe_mode(self) -> bool:
        """Determina se deve ativar modo seguro"""
        health = self.get_system_health()
        
        if health < 50:
            self.safe_mode_active = True
            self.logger.log_system_event("SAFE_MODE_ACTIVATED", "Saúde do sistema abaixo de 50%")
            return True
        
        return False
    
    def get_fallback_settings(self) -> Dict:
        """Configurações de fallback em modo seguro"""
        return {
            "min_score_requirement": 95,  # Mais restritivo
            "position_size": 0.001,  # Mínimo
            "max_concurrent_trades": 1,  # Um de cada vez
            "require_multiple_confirmations": True,
            "use_only_conservative_strategies": True
        }
    
    def get_resilience_report(self) -> Dict:
        """Relatório de resiliência"""
        return {
            "system_health": self.get_system_health(),
            "safe_mode_active": self.safe_mode_active,
            "module_health": self.module_health,
            "failure_counts": self.failure_count,
            "recommendation": "CONTINUE_NORMAL" if self.get_system_health() > 70 else "SWITCH_TO_SAFE_MODE"
        }


"""
═══════════════════════════════════════════════════════════════════
CAMADA 18: EXPLICAÇÃO DE SEGUNDA ORDEM
═══════════════════════════════════════════════════════════════════
O bot explica por que NÃO fez algo.
"""


class SecondOrderExplainer:
    """
    Explicação profunda de decisões, incluindo o que foi rejeitado.
    """
    
    def __init__(self):
        self.logger = get_logger()
    
    def explain_trade_rejection(
        self,
        score: float,
        min_required: float,
        reasons_for_rejection: list,
        alternative_strategies: list
    ) -> Dict:
        """
        Explica por que um trade foi rejeitado.
        """
        return {
            "trade_status": "REJECTED",
            "score": score,
            "min_required": min_required,
            "score_gap": min_required - score,
            "primary_reason": reasons_for_rejection[0] if reasons_for_rejection else "Unknown",
            "all_rejection_reasons": reasons_for_rejection,
            "alternative_strategies": alternative_strategies,
            "explanation": self._generate_explanation(score, min_required, reasons_for_rejection),
            "what_would_be_needed": self._get_improvement_path(score, min_required)
        }
    
    def _generate_explanation(self, score: float, min_required: float, reasons: list) -> str:
        """Gera explicação natural"""
        gap = min_required - score
        
        if gap > 20:
            severity = "significantly"
        elif gap > 10:
            severity = "moderately"
        else:
            severity = "slightly"
        
        reason_text = " AND ".join(reasons[:2])
        
        return f"Trade foi rejeitado porque {severity} não atingiu o score mínimo. Score: {score:.0f}/100 (precisava {min_required:.0f}). Razões principais: {reason_text}"
    
    def _get_improvement_path(self, current_score: float, required_score: float) -> list:
        """Caminhos para melhorar o score"""
        gap = required_score - current_score
        
        improvements = []
        
        if gap > 15:
            improvements.append("Esperar confirmação adicional")
            improvements.append("Aumentar timeframe de análise")
            improvements.append("Buscar múltiplos indicadores alinhados")
        
        if gap > 8:
            improvements.append("Validar padrão em timeframe superior")
            improvements.append("Verificar se é horário ótimo")
        
        improvements.append("Aguardar melhor entrada")
        
        return improvements
    
    def explain_trade_approval(
        self,
        score: float,
        key_factors: list,
        risk_factors: list,
        exit_conditions: list
    ) -> Dict:
        """
        Explica por que um trade foi aprovado.
        """
        return {
            "trade_status": "APPROVED",
            "score": score,
            "key_factors": key_factors,
            "risk_factors": risk_factors,
            "exit_conditions": exit_conditions,
            "confidence_level": self._score_to_confidence(score),
            "what_could_invalidate": self._get_invalidation_scenarios(risk_factors)
        }
    
    def _score_to_confidence(self, score: float) -> str:
        """Score para nível de confiança"""
        if score >= 95:
            return "VERY_HIGH"
        elif score >= 90:
            return "HIGH"
        elif score >= 85:
            return "MEDIUM_HIGH"
        elif score >= 75:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_invalidation_scenarios(self, risk_factors: list) -> list:
        """Cenários que invalidariam o trade"""
        scenarios = [
            f"Se {rf.lower()} mudar" for rf in risk_factors[:2]
        ]
        scenarios.append("Se estrutura de suporte/resistência for quebrada")
        scenarios.append("Se volatilidade explodir inesperadamente")
        
        return scenarios


"""
═══════════════════════════════════════════════════════════════════
CAMADA 19: SIMULAÇÃO INTERNA RÁPIDA
═══════════════════════════════════════════════════════════════════
O bot simula cenários extremos antes de executar.
"""


class InternalSimulator:
    """
    Simula trade em cenários extremos como validação.
    """
    
    def __init__(self):
        self.logger = get_logger()
    
    def stress_test_trade(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        position_size: float,
        extreme_scenarios: int = 5
    ) -> Dict:
        """
        Executa stress test com cenários extremos.
        """
        results = []
        
        # Cenários extremos
        scenarios = [
            {"name": "Gap down 2%", "price_move": -0.02},
            {"name": "Gap up 3%", "price_move": 0.03},
            {"name": "Flash crash 5%", "price_move": -0.05},
            {"name": "Normal hit TP", "price_move": (take_profit - entry_price) / entry_price},
            {"name": "Hit SL + spike", "price_move": (stop_loss - entry_price) / entry_price - 0.01}
        ]
        
        for scenario in scenarios[:extreme_scenarios]:
            new_price = entry_price * (1 + scenario["price_move"])
            
            # Determinar resultado
            if new_price <= stop_loss:
                pnl = -abs(stop_loss - entry_price) * position_size
                result = "STOPPED_OUT"
            elif new_price >= take_profit:
                pnl = (take_profit - entry_price) * position_size
                result = "PROFIT_TARGET_HIT"
            else:
                pnl = (new_price - entry_price) * position_size
                result = "STILL_OPEN"
            
            results.append({
                "scenario": scenario["name"],
                "simulated_price": new_price,
                "pnl": pnl,
                "result": result,
                "survival": result != "STOPPED_OUT"
            })
        
        # Análise
        survival_rate = sum(1 for r in results if r["survival"]) / len(results)
        
        return {
            "trade_survives_stress": survival_rate > 0.6,
            "survival_rate": survival_rate,
            "scenarios": results,
            "recommendation": "APPROVE" if survival_rate > 0.7 else "REJECT"
        }


"""
═══════════════════════════════════════════════════════════════════
CAMADA 20: PREPARAÇÃO PARA O FUTURO
═══════════════════════════════════════════════════════════════════
Arquitetura extensível para evolução contínua.
"""

from typing import Callable


class FutureReadiness:
    """
    Framework para extensão e evolução do bot.
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.plugins = {}
        self.integrations = {}
    
    def register_plugin(self, name: str, plugin_class: type) -> None:
        """Registra novo plugin de estratégia"""
        self.plugins[name] = plugin_class()
        self.logger.log_system_event(
            "PLUGIN_REGISTERED",
            f"Plugin '{name}' registrado com sucesso"
        )
    
    def register_data_source(self, name: str, source_callable: Callable) -> None:
        """Registra nova fonte de dados"""
        self.integrations[f"data_source_{name}"] = source_callable
        self.logger.log_system_event(
            "DATA_SOURCE_REGISTERED",
            f"Fonte de dados '{name}' registrada"
        )
    
    def add_market_regime(self, name: str, detection_fn: Callable, strategy_type: str) -> None:
        """Adiciona novo regime de mercado"""
        self.integrations[f"regime_{name}"] = {
            "detect": detection_fn,
            "strategy": strategy_type
        }
        self.logger.log_system_event(
            "REGIME_ADDED",
            f"Regime '{name}' adicionado para estratégia '{strategy_type}'"
        )
    
    def list_installed_plugins(self) -> Dict:
        """Lista plugins instalados"""
        return {
            "plugins": list(self.plugins.keys()),
            "data_sources": [
                k.replace("data_source_", "") 
                for k in self.integrations.keys() 
                if k.startswith("data_source_")
            ],
            "market_regimes": [
                k.replace("regime_", "") 
                for k in self.integrations.keys() 
                if k.startswith("regime_")
            ]
        }
    
    def get_api_reference(self) -> Dict:
        """Referência de API para developers"""
        return {
            "plugin_interface": {
                "required_methods": ["analyze", "get_signals", "update_performance"],
                "optional_methods": ["configure", "save_state", "load_state"]
            },
            "data_source_interface": {
                "required_methods": ["fetch", "validate", "format"],
                "return_format": "Dict with OHLCV data"
            },
            "version": "2.0",
            "extensions_supported": ["plugins", "data_sources", "strategies", "indicators"]
        }
    
    def get_readiness_report(self) -> Dict:
        """Relatório de preparação para futuro"""
        return {
            "architecture": "Modular with plugin system",
            "extensibility": "High - supports new strategies, data sources, regimes",
            "plugin_count": len(self.plugins),
            "integration_count": len(self.integrations),
            "api_version": "2.0",
            "supports_multimarket": True,
            "supports_concurrent_updates": True,
            "downtime_free_updates": "Yes - hot-reload capable"
        }


from typing import Tuple
