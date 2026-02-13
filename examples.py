"""
═══════════════════════════════════════════════════════════════════
EXEMPLOS DE USO - TRADING BOT
═══════════════════════════════════════════════════════════════════
Exemplos práticos de como usar cada módulo do bot.
"""

import sys
sys.path.insert(0, '.')

from core import (
    MarketAnalyzer,
    PatternEngine,
    ScoreEngine,
    RiskManager,
    MemoryEngine,
    LearningEngine,
    get_logger
)
import pandas as pd
from datetime import datetime


def example_market_analysis():
    """
    Exemplo: Análise completa de mercado
    """
    print("═" * 60)
    print("EXEMPLO: MARKET ANALYZER")
    print("═" * 60)
    
    # Criar dados de exemplo
    dates = pd.date_range(start='2024-01-01', periods=300, freq='1h')
    df_h1 = pd.DataFrame({
        'timestamp': dates,
        'open': 100 + pd.Series(range(300)).apply(lambda x: x * 0.1),
        'high': 101 + pd.Series(range(300)).apply(lambda x: x * 0.1),
        'low': 99 + pd.Series(range(300)).apply(lambda x: x * 0.1),
        'close': 100.5 + pd.Series(range(300)).apply(lambda x: x * 0.1),
        'volume': 1000000
    })
    
    # Replicar para outros timeframes (simplificado)
    df_m5 = df_h1.copy()
    df_m15 = df_h1.copy()
    df_h4 = df_h1.copy()
    df_d1 = df_h1.copy()
    
    # Inicializar analyzer
    analyzer = MarketAnalyzer()
    
    # Análise completa
    analysis = analyzer.analyze_complete_market(
        df_m5=df_m5,
        df_m15=df_m15,
        df_h1=df_h1,
        df_h4=df_h4,
        df_d1=df_d1,
        current_price=130.0
    )
    
    print(f"\nTendência Consenso: {analysis['trend']['consensus']['direction']}")
    print(f"Força: {analysis['trend']['consensus']['strength']:.1f}")
    print(f"Momentum Score: {analysis['momentum']['score']}")
    print(f"Health Score: {analysis['market_health_score']}")
    print(f"Sessão: {analysis['session']['current']}")


def example_pattern_detection():
    """
    Exemplo: Detecção de padrões
    """
    print("\n" + "═" * 60)
    print("EXEMPLO: PATTERN ENGINE")
    print("═" * 60)
    
    # Criar dados com padrão bullish engulfing
    df = pd.DataFrame({
        'open': [100, 99, 98, 100, 101],
        'high': [101, 100, 99, 102, 103],
        'low': [99, 98, 97, 99, 100],
        'close': [99.5, 98.5, 99.8, 101.5, 102],
        'volume': [1000000] * 5
    })
    
    engine = PatternEngine()
    
    patterns = engine._detect_candle_patterns(df)
    
    print(f"\nPadrões detectados: {len(patterns)}")
    for pattern in patterns:
        print(f"  • {pattern['type']}: {pattern['direction']} (Força: {pattern['strength']})")


def example_score_calculation():
    """
    Exemplo: Cálculo de score
    """
    print("\n" + "═" * 60)
    print("EXEMPLO: SCORE ENGINE")
    print("═" * 60)
    
    # Análises simuladas
    market_analysis = {
        "trend": {
            "consensus": {"direction": "BULLISH", "strength": 75},
            "h1": {"ema_alignment": True, "strength": 70}
        },
        "momentum": {"score": 65, "direction": "BULLISH", "strength": "MODERATE"},
        "structure": {"strength": 70},
        "volatility": {"classification": "NORMAL", "volatility_ratio": 1.0},
        "liquidity": {"score": 80},
        "session": {"is_favorable": True, "quality_score": 85},
        "movement_quality": {"classification": "STRONG", "quality_score": 75},
        "temporal_context": {"day_quality": 85},
        "volume": {"available": True, "trend_confirmation": True}
    }
    
    pattern_analysis = {
        "candle_patterns": {
            "h1": [{"type": "ENGULFING_BULLISH", "strength": 75, "confidence": 70}]
        },
        "chart_patterns": {"h1": []},
        "primary_signal": {"type": "ENGULFING_BULLISH", "strength": 75}
    }
    
    risk_analysis = {
        "current_drawdown_pct": 5,
        "exposure_pct": 30,
        "potential_profit": 150,
        "potential_loss": 50
    }
    
    learning_insights = {
        "similar_pattern_winrate": 65,
        "recent_consecutive_losses": 0
    }
    
    # Calcular score
    engine = ScoreEngine()
    result = engine.calculate_comprehensive_score(
        market_analysis=market_analysis,
        pattern_analysis=pattern_analysis,
        risk_analysis=risk_analysis,
        learning_insights=learning_insights
    )
    
    print(f"\nScore Total: {result.total_score}/100")
    print(f"Recomendação: {result.recommendation}")
    print(f"Confiança: {result.confidence:.1f}%")
    print(f"Risco/Retorno: {result.risk_reward_ratio:.2f}")
    
    print("\nComponentes:")
    for component, value in result.components.items():
        print(f"  {component}: {value:.1f}")
    
    if result.reasons:
        print("\nRazões:")
        for reason in result.reasons:
            print(f"  ✓ {reason}")
    
    if result.warnings:
        print("\nAvisos:")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")


def example_risk_management():
    """
    Exemplo: Gestão de risco
    """
    print("\n" + "═" * 60)
    print("EXEMPLO: RISK MANAGER")
    print("═" * 60)
    
    risk = RiskManager()
    
    # Verificar se pode operar
    can_trade, reason = risk.can_trade()
    print(f"\nPode operar? {can_trade}")
    print(f"Razão: {reason}")
    
    # Calcular tamanho de posição
    position_size = risk.calculate_position_size(
        account_balance=10000,
        stop_loss_distance=0.02,
        current_price=100
    )
    print(f"\nTamanho de posição recomendado: {position_size}")
    
    # Simular trade
    risk.record_trade(
        profit_loss=50.0,
        was_win=True,
        trade_details={"symbol": "BTCUSDT", "side": "BUY"}
    )
    
    # Métricas
    metrics = risk.get_risk_metrics()
    print(f"\nEstado de Risco: {metrics.risk_state}")
    print(f"P&L Diário: ${metrics.daily_pnl:.2f}")
    print(f"Win Rate: {metrics.win_rate:.1f}%")


def example_memory_and_learning():
    """
    Exemplo: Memória e aprendizado
    """
    print("\n" + "═" * 60)
    print("EXEMPLO: MEMORY & LEARNING")
    print("═" * 60)
    
    memory = MemoryEngine()
    
    # Estatísticas
    stats = memory.get_statistics(days=30)
    print(f"\nEstatísticas (30 dias):")
    print(f"  Total Trades: {stats['total_trades']}")
    print(f"  Win Rate: {stats['win_rate']:.1f}%")
    print(f"  P&L Total: ${stats['total_pnl']:.2f}")
    
    # Melhores padrões
    best = memory.get_best_patterns(min_trades=3)
    print(f"\nMelhores Padrões:")
    for pattern in best[:3]:
        print(f"  • {pattern['pattern']}: {pattern['win_rate']:.1f}% WR")
    
    # Learning engine
    learning = LearningEngine(memory)
    
    context = {
        "primary_pattern": "ENGULFING_BULLISH",
        "market_trend": "BULLISH",
        "volatility_level": "NORMAL",
        "session": "LONDON"
    }
    
    insights = learning.get_learning_insights(context)
    print(f"\nInsights de Aprendizado:")
    print(f"  Padrão Similar WR: {insights['similar_pattern_winrate']:.1f}%")
    print(f"  Contexto Favorável: {insights['context_favorable']}")
    print(f"  Hot Streak: {insights['hot_streak']}")
    
    # Recomendações
    recommendations = insights['recommended_adjustments']
    if recommendations:
        print(f"\nRecomendações:")
        for rec in recommendations[:3]:
            print(f"  • {rec}")


def example_logger():
    """
    Exemplo: Sistema de logs
    """
    print("\n" + "═" * 60)
    print("EXEMPLO: LOGGER")
    print("═" * 60)
    
    logger = get_logger()
    
    # Log de trade
    logger.log_trade_entry(
        trade_id="TRADE_001",
        symbol="BTCUSDT",
        side="BUY",
        price=50000.0,
        quantity=0.01,
        score=92,
        confidence=85.5,
        reason="Score alto + padrão bullish"
    )
    
    logger.log_trade_exit(
        trade_id="TRADE_001",
        symbol="BTCUSDT",
        exit_price=50500.0,
        pnl=50.0,
        pnl_pct=1.0,
        duration=3600,
        reason="Take profit atingido"
    )
    
    # Log de erro
    logger.log_error(
        error_type="API_ERROR",
        message="Timeout na requisição",
        context={"symbol": "BTCUSDT", "attempt": 1}
    )
    
    # Log de decisão
    logger.log_decision(
        score=85,
        recommendation="ALERT_ONLY",
        reasons=["Tendência clara", "Padrão válido"],
        warnings=["Score abaixo de 90"]
    )
    
    print("\n✓ Logs salvos em logs/")


def run_all_examples():
    """
    Executa todos os exemplos.
    """
    example_market_analysis()
    example_pattern_detection()
    example_score_calculation()
    example_risk_management()
    example_memory_and_learning()
    example_logger()
    
    print("\n" + "═" * 60)
    print("✅ TODOS OS EXEMPLOS EXECUTADOS")
    print("═" * 60)


if __name__ == "__main__":
    run_all_examples()
