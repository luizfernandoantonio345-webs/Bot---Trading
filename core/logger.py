"""
═══════════════════════════════════════════════════════════════════
LOGGER - SISTEMA DE LOGS PROFISSIONAL
═══════════════════════════════════════════════════════════════════
Logs estruturados com rotação automática para trades, erros e learning.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Dict, Any
import json


class TradingLogger:
    """
    Sistema de logs profissional com múltiplos níveis e rotação.
    """
    
    def __init__(self, logs_dir: str = "logs"):
        """
        Inicializa sistema de logs.
        
        Args:
            logs_dir: Diretório para armazenar logs
        """
        self.logs_dir = logs_dir
        
        # Criar diretório se não existe
        os.makedirs(logs_dir, exist_ok=True)
        
        # Inicializar loggers
        self.trade_logger = self._setup_logger(
            "trades",
            os.path.join(logs_dir, "trades.log"),
            max_bytes=10*1024*1024,  # 10MB
            backup_count=5
        )
        
        self.error_logger = self._setup_logger(
            "errors",
            os.path.join(logs_dir, "errors.log"),
            max_bytes=5*1024*1024,  # 5MB
            backup_count=3
        )
        
        self.learning_logger = self._setup_logger(
            "learning",
            os.path.join(logs_dir, "learning.log"),
            max_bytes=5*1024*1024,  # 5MB
            backup_count=3
        )
        
        self.system_logger = self._setup_logger(
            "system",
            os.path.join(logs_dir, "system.log"),
            max_bytes=10*1024*1024,  # 10MB
            backup_count=5
        )
        
        print(f"✅ Sistema de logs inicializado | Dir: {logs_dir}")
    
    def _setup_logger(
        self,
        name: str,
        log_file: str,
        max_bytes: int = 10*1024*1024,
        backup_count: int = 5
    ) -> logging.Logger:
        """
        Configura logger individual com rotação.
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Handler com rotação
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Formato detalhado
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Também logar no console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_trade(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        entry_price: float,
        exit_price: float = None,
        pnl: float = None,
        result: str = "OPEN",
        details: Dict = None
    ):
        """
        Log de trade.
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl": pnl,
            "result": result,
            "details": details or {}
        }
        
        self.trade_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_trade_entry(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        price: float,
        quantity: float,
        score: int,
        confidence: float,
        reason: str
    ):
        """
        Log específico de entrada em trade.
        """
        msg = (
            f"ENTRADA | {trade_id} | {symbol} | {side} | "
            f"Preço: {price:.4f} | Qtd: {quantity} | "
            f"Score: {score} | Conf: {confidence:.1f}% | "
            f"Razão: {reason}"
        )
        
        self.trade_logger.info(msg)
    
    def log_trade_exit(
        self,
        trade_id: str,
        symbol: str,
        exit_price: float,
        pnl: float,
        pnl_pct: float,
        duration: int,
        reason: str
    ):
        """
        Log específico de saída de trade.
        """
        result_emoji = "✅" if pnl > 0 else "❌"
        
        msg = (
            f"{result_emoji} SAÍDA | {trade_id} | {symbol} | "
            f"Preço: {exit_price:.4f} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%) | "
            f"Duração: {duration}s | Razão: {reason}"
        )
        
        self.trade_logger.info(msg)
    
    def log_error(
        self,
        error_type: str,
        message: str,
        context: Dict = None,
        exception: Exception = None
    ):
        """
        Log de erro.
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message,
            "context": context or {},
            "exception": str(exception) if exception else None
        }
        
        self.error_logger.error(json.dumps(log_data, ensure_ascii=False))
        
        # Também logar exceção completa se houver
        if exception:
            self.error_logger.exception(exception)
    
    def log_learning_update(
        self,
        insights: Dict,
        adjustments: list
    ):
        """
        Log de atualização de aprendizado.
        """
        msg = (
            f"LEARNING UPDATE | "
            f"Insights: {len(insights)} | "
            f"Ajustes: {len(adjustments)}"
        )
        
        self.learning_logger.info(msg)
        self.learning_logger.info(f"Detalhes: {json.dumps(insights, indent=2)}")
    
    def log_pattern_analysis(
        self,
        pattern: str,
        winrate: float,
        total_trades: int,
        status: str
    ):
        """
        Log de análise de padrão.
        """
        msg = (
            f"PADRÃO ANALISADO | {pattern} | "
            f"WR: {winrate:.1f}% | Trades: {total_trades} | "
            f"Status: {status}"
        )
        
        self.learning_logger.info(msg)
    
    def log_risk_event(
        self,
        event_type: str,
        message: str,
        metrics: Dict = None
    ):
        """
        Log de evento de risco.
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "metrics": metrics or {}
        }
        
        self.system_logger.warning(json.dumps(log_data, ensure_ascii=False))
    
    def log_system_start(self, config: Dict):
        """
        Log de inicialização do sistema.
        """
        self.system_logger.info("═" * 60)
        self.system_logger.info("🚀 BOT TRADING INICIADO")
        self.system_logger.info("═" * 60)
        self.system_logger.info(f"Configuração: {json.dumps(config, indent=2)}")
    
    def log_system_stop(self, reason: str = "Manual"):
        """
        Log de parada do sistema.
        """
        self.system_logger.info("═" * 60)
        self.system_logger.info(f"🛑 BOT TRADING PARADO | Razão: {reason}")
        self.system_logger.info("═" * 60)
    
    def log_daily_summary(self, stats: Dict):
        """
        Log de resumo diário.
        """
        self.system_logger.info("=" * 60)
        self.system_logger.info("📊 RESUMO DIÁRIO")
        self.system_logger.info("=" * 60)
        self.system_logger.info(f"Total Trades: {stats.get('total_trades', 0)}")
        self.system_logger.info(f"Wins: {stats.get('wins', 0)} | Losses: {stats.get('losses', 0)}")
        self.system_logger.info(f"Winrate: {stats.get('winrate', 0):.1f}%")
        self.system_logger.info(f"P&L: ${stats.get('pnl', 0):.2f}")
        self.system_logger.info(f"Profit Factor: {stats.get('profit_factor', 0):.2f}")
        self.system_logger.info("=" * 60)
    
    def log_decision(
        self,
        score: int,
        recommendation: str,
        reasons: list,
        warnings: list
    ):
        """
        Log de decisão de trading.
        """
        msg = f"DECISÃO | Score: {score} | Rec: {recommendation}"
        
        self.system_logger.info(msg)
        
        if reasons:
            self.system_logger.info(f"  Razões: {'; '.join(reasons)}")
        
        if warnings:
            self.system_logger.warning(f"  Avisos: {'; '.join(warnings)}")
    
    def log_market_analysis(self, analysis: Dict):
        """
        Log de análise de mercado.
        """
        msg = (
            f"ANÁLISE | "
            f"Trend: {analysis.get('trend', {}).get('consensus', {}).get('direction', 'N/A')} | "
            f"Momentum: {analysis.get('momentum', {}).get('score', 0)} | "
            f"Health: {analysis.get('market_health_score', 0)}"
        )
        
        self.system_logger.info(msg)
    
    def log_execution(
        self,
        action: str,
        symbol: str,
        details: str,
        success: bool = True
    ):
        """
        Log de execução de ordens.
        """
        status = "✅" if success else "❌"
        
        msg = f"{status} EXECUÇÃO | {action} | {symbol} | {details}"
        
        if success:
            self.system_logger.info(msg)
        else:
            self.system_logger.error(msg)


# Instância global
_logger_instance = None


def get_logger(logs_dir: str = "logs") -> TradingLogger:
    """
    Retorna instância singleton do logger.
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = TradingLogger(logs_dir)
    
    return _logger_instance


if __name__ == "__main__":
    print("Trading Logger - Sistema de Logs Profissional")
    print("Módulo pronto para integração")
