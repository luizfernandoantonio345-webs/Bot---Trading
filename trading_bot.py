"""
═══════════════════════════════════════════════════════════════════
TRADING BOT - ORQUESTRADOR PRINCIPAL
═══════════════════════════════════════════════════════════════════
Sistema de trading profissional com análise multicamadas,
gestão de risco rigorosa, aprendizado automático e execução real.

ATENÇÃO: Este bot opera em CONTA REAL. 
Configure corretamente antes de executar.
═══════════════════════════════════════════════════════════════════
"""

import time
import os
import sys
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
import yaml
import pandas as pd
import ccxt

# Importar módulos do core
from core.market_analyzer import MarketAnalyzer
from core.pattern_engine import PatternEngine
from core.score_engine import ScoreEngine, ScoreWeights
from core.risk_manager import RiskManager, RiskLimits
from core.execution_engine import BinanceExecutor, OrderSide
from core.memory_engine import MemoryEngine, TradeRecord
from core.learning_engine import LearningEngine
from core.logger import get_logger


class TradingBot:
    """
    Bot de trading profissional com sistema completo de decisão.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Inicializa bot com configurações.
        """
        print("═" * 70)
        print("🤖 TRADING BOT PROFISSIONAL - INICIALIZANDO")
        print("═" * 70)
        
        # Carregar configurações
        self.config = self._load_config(config_dir)
        
        # Inicializar logger
        self.logger = get_logger()
        self.logger.log_system_start(self.config)
        
        # Inicializar módulos
        self._init_modules()
        
        # Estado
        self.is_running = False
        self.current_trade = None
        self.loop_count = 0
        
        print("✅ Bot inicializado com sucesso")
        print("═" * 70)
    
    def _load_config(self, config_dir: str) -> Dict:
        """
        Carrega todas as configurações.
        """
        # API Keys
        env_file = os.path.join(config_dir, "api_keys.env")
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Risk Limits
        risk_file = os.path.join(config_dir, "risk_limits.yaml")
        with open(risk_file, 'r') as f:
            risk_config = yaml.safe_load(f)
        
        # Weights
        weights_file = os.path.join(config_dir, "weights.yaml")
        with open(weights_file, 'r') as f:
            weights_config = yaml.safe_load(f)
        
        config = {
            "api_key": os.getenv("BINANCE_API_KEY", ""),
            "api_secret": os.getenv("BINANCE_API_SECRET", ""),
            "use_testnet": os.getenv("USE_TESTNET", "True").lower() == "true",
            "is_futures": os.getenv("IS_FUTURES", "True").lower() == "true",
            "primary_symbol": os.getenv("PRIMARY_SYMBOL", "BTCUSDT"),
            
            "risk_limits": risk_config,
            "weights": weights_config
        }
        
        return config
    
    def _init_modules(self):
        """
        Inicializa todos os módulos do bot.
        """
        print("⚙️  Inicializando módulos...")
        
        # Market Analyzer
        self.market_analyzer = MarketAnalyzer()
        print("  ✓ Market Analyzer")
        
        # Pattern Engine
        self.pattern_engine = PatternEngine()
        print("  ✓ Pattern Engine")
        
        # Score Engine
        score_weights = ScoreWeights(
            trend=self.config["weights"]["trend_weight"],
            momentum=self.config["weights"]["momentum_weight"],
            confirmations=self.config["weights"]["confirmations_weight"],
            risk_quality=self.config["weights"]["risk_quality_weight"],
            context=self.config["weights"]["context_weight"]
        )
        self.score_engine = ScoreEngine(custom_weights=score_weights.__dict__)
        print("  ✓ Score Engine")
        
        # Risk Manager
        risk_limits = RiskLimits(**self.config["risk_limits"])
        self.risk_manager = RiskManager(limits=risk_limits)
        print("  ✓ Risk Manager")
        
        # Execution Engine
        self.executor = BinanceExecutor(
            api_key=self.config["api_key"],
            api_secret=self.config["api_secret"],
            use_testnet=self.config["use_testnet"],
            is_futures=self.config["is_futures"]
        )
        print("  ✓ Execution Engine")
        
        # Memory Engine
        self.memory = MemoryEngine()
        print("  ✓ Memory Engine")
        
        # Learning Engine
        self.learning = LearningEngine(self.memory)
        print("  ✓ Learning Engine")
        
        # Exchange (CCXT para dados)
        self.exchange = ccxt.binance({
            'apiKey': self.config["api_key"],
            'secret': self.config["api_secret"],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future' if self.config["is_futures"] else 'spot'
            }
        })
        
        if self.config["use_testnet"]:
            self.exchange.set_sandbox_mode(True)
        
        print("  ✓ Exchange (CCXT)")
    
    def run(self):
        """
        Loop principal do bot.
        """
        self.is_running = True
        
        print("\n🚀 BOT ATIVO - OPERANDO EM CONTA REAL")
        print("   Pressione Ctrl+C para parar\n")
        
        try:
            while self.is_running:
                self.loop_count += 1
                
                # Análise e decisão
                self._trading_loop()
                
                # Atualizar learning a cada 10 loops
                if self.loop_count % 10 == 0:
                    self.learning.update_insights()
                
                # Aguardar antes do próximo loop
                time.sleep(60)  # 60 segundos
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupção manual detectada")
            self.stop()
        
        except Exception as e:
            self.logger.log_error("FATAL_ERROR", "Erro fatal no loop principal", exception=e)
            self.stop()
    
    def _trading_loop(self):
        """
        Loop de análise e decisão de trading.
        """
        try:
            symbol = self.config["primary_symbol"]
            
            # ═══════════════════════════════════════
            # 1. VERIFICAR SE PODE OPERAR
            # ═══════════════════════════════════════
            can_trade, reason = self.risk_manager.can_trade()
            
            if not can_trade:
                self.logger.log_risk_event("TRADING_BLOCKED", reason)
                return
            
            # ═══════════════════════════════════════
            # 2. OBTER DADOS DE MERCADO
            # ═══════════════════════════════════════
            market_data = self._fetch_market_data(symbol)
            
            if not market_data:
                return
            
            # ═══════════════════════════════════════
            # 3. ANÁLISE DE MERCADO
            # ═══════════════════════════════════════
            market_analysis = self.market_analyzer.analyze_complete_market(
                df_m5=market_data['m5'],
                df_m15=market_data['m15'],
                df_h1=market_data['h1'],
                df_h4=market_data['h4'],
                df_d1=market_data['d1'],
                current_price=market_data['current_price']
            )
            
            self.logger.log_market_analysis(market_analysis)
            
            # ═══════════════════════════════════════
            # 4. ANÁLISE DE PADRÕES
            # ═══════════════════════════════════════
            # Identificar suporte/resistência (simplificado)
            sr_levels = self._calculate_support_resistance(market_data['h1'])
            
            pattern_analysis = self.pattern_engine.detect_all_patterns(
                df_m15=market_data['m15'],
                df_h1=market_data['h1'],
                df_h4=market_data['h4'],
                support_resistance=sr_levels
            )
            
            # ═══════════════════════════════════════
            # 5. INSIGHTS DE APRENDIZADO
            # ═══════════════════════════════════════
            current_context = {
                "primary_pattern": pattern_analysis.get("primary_signal", {}).get("type"),
                "market_trend": market_analysis["trend"]["consensus"]["direction"],
                "volatility_level": market_analysis["volatility"]["classification"],
                "session": market_analysis["session"]["current"]
            }
            
            learning_insights = self.learning.get_learning_insights(current_context)
            
            # ═══════════════════════════════════════
            # 6. CÁLCULO DE SCORE
            # ═══════════════════════════════════════
            risk_analysis = {
                "current_drawdown_pct": self.risk_manager.state["current_drawdown_pct"],
                "exposure_pct": self.risk_manager.state["current_exposure_pct"],
                "potential_profit": 100,  # Estimativa
                "potential_loss": 50      # Estimativa
            }
            
            score_result = self.score_engine.calculate_comprehensive_score(
                market_analysis=market_analysis,
                pattern_analysis=pattern_analysis,
                risk_analysis=risk_analysis,
                learning_insights=learning_insights
            )
            
            # Log da decisão
            self.logger.log_decision(
                score=score_result.total_score,
                recommendation=score_result.recommendation,
                reasons=score_result.reasons,
                warnings=score_result.warnings
            )
            
            # Exibir score
            print(f"\n⭐ SCORE: {score_result.total_score}/100 | {score_result.recommendation}")
            
            # ═══════════════════════════════════════
            # 7. DECISÃO DE EXECUÇÃO
            # ═══════════════════════════════════════
            if score_result.recommendation == "EXECUTE":
                self._execute_trade(
                    symbol=symbol,
                    market_analysis=market_analysis,
                    pattern_analysis=pattern_analysis,
                    score_result=score_result,
                    current_price=market_data['current_price']
                )
            
            elif score_result.recommendation == "ALERT_ONLY":
                print(f"⚠️  ALERTA: Setup promissor mas score < 90")
                print(f"   Razões: {', '.join(score_result.reasons[:2])}")
            
        except Exception as e:
            self.logger.log_error("LOOP_ERROR", "Erro no loop de trading", exception=e)
    
    def _fetch_market_data(self, symbol: str) -> Optional[Dict]:
        """
        Busca dados de mercado de múltiplos timeframes.
        """
        try:
            data = {}
            
            # Timeframes
            timeframes = {
                'm5': '5m',
                'm15': '15m',
                'h1': '1h',
                'h4': '4h',
                'd1': '1d'
            }
            
            for key, tf in timeframes.items():
                ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=300)
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                data[key] = df
            
            # Preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            data['current_price'] = ticker['last']
            
            return data
        
        except Exception as e:
            self.logger.log_error("DATA_FETCH_ERROR", f"Erro ao buscar dados: {symbol}", exception=e)
            return None
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """
        Calcula níveis de suporte e resistência (simplificado).
        """
        # Usar últimos 50 candles
        recent = df.tail(50)
        
        # Resistências (topos)
        resistances = sorted(recent['high'].nlargest(3).tolist(), reverse=True)
        
        # Suportes (fundos)
        supports = sorted(recent['low'].nsmallest(3).tolist())
        
        return {
            "resistance": resistances,
            "support": supports
        }
    
    def _execute_trade(
        self,
        symbol: str,
        market_analysis: Dict,
        pattern_analysis: Dict,
        score_result,
        current_price: float
    ):
        """
        Executa trade.
        """
        try:
            # Determinar direção
            trend_direction = market_analysis["trend"]["consensus"]["direction"]
            
            if trend_direction == "BULLISH":
                side = OrderSide.BUY
            elif trend_direction == "BEARISH":
                side = OrderSide.SELL
            else:
                print("⚠️  Tendência neutra - não executar")
                return
            
            # Calcular tamanho de posição
            account_balance = self.executor.get_account_balance()
            usdt_balance = account_balance.get('USDT', 0)
            
            if usdt_balance < 100:
                print(f"⚠️  Saldo insuficiente: ${usdt_balance:.2f}")
                return
            
            # ATR para stop loss
            atr = market_analysis["volatility"]["atr_m15"]
            stop_distance = atr * 2
            
            position_size = self.risk_manager.calculate_position_size(
                account_balance=usdt_balance,
                stop_loss_distance=stop_distance,
                current_price=current_price
            )
            
            if position_size == 0:
                print("⚠️  Tamanho de posição = 0 (risco bloqueado)")
                return
            
            # Executar ordem
            print(f"\n🎯 EXECUTANDO: {side.value} {position_size} {symbol}")
            
            order = self.executor.place_market_order(
                symbol=symbol,
                side=side,
                quantity=position_size
            )
            
            # Calcular stop loss e take profit
            if side == OrderSide.BUY:
                stop_loss = current_price - (atr * 2)
                take_profit = current_price + (atr * 3)
            else:
                stop_loss = current_price + (atr * 2)
                take_profit = current_price - (atr * 3)
            
            # Colocar stop loss
            stop_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
            self.executor.place_stop_loss(
                symbol=symbol,
                side=stop_side,
                quantity=position_size,
                stop_price=stop_loss
            )
            
            # Log
            self.logger.log_trade_entry(
                trade_id=order.order_id,
                symbol=symbol,
                side=side.value,
                price=order.executed_price,
                quantity=position_size,
                score=score_result.total_score,
                confidence=score_result.confidence,
                reason=f"Score: {score_result.total_score}"
            )
            
            # Armazenar trade atual
            self.current_trade = {
                "order": order,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "entry_time": datetime.now()
            }
            
            print(f"✅ TRADE ABERTO")
            print(f"   Entry: {order.executed_price:.4f}")
            print(f"   Stop: {stop_loss:.4f}")
            print(f"   Target: {take_profit:.4f}")
        
        except Exception as e:
            self.logger.log_error("EXECUTION_ERROR", "Erro ao executar trade", exception=e)
    
    def stop(self):
        """
        Para o bot graciosamente.
        """
        print("\n🛑 Parando bot...")
        
        self.is_running = False
        
        # Fechar posições abertas (se configurado)
        # ...
        
        # Log final
        stats = self.memory.get_statistics(days=1)
        self.logger.log_daily_summary(stats)
        self.logger.log_system_stop()
        
        print("✅ Bot parado com sucesso")


def main():
    """
    Função principal.
    """
    # Verificar se configuração existe
    if not os.path.exists("config/api_keys.env"):
        print("❌ ERRO: config/api_keys.env não encontrado")
        print("   Configure suas API keys antes de executar")
        sys.exit(1)
    
    # Inicializar bot
    bot = TradingBot()
    
    # Executar
    bot.run()


if __name__ == "__main__":
    main()
