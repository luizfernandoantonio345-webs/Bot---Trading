"""
═══════════════════════════════════════════════════════════════════
UTILS - UTILITÁRIOS E FERRAMENTAS
═══════════════════════════════════════════════════════════════════
Scripts úteis para análise, backup e manutenção.
"""

import sys
import argparse
from datetime import datetime, timedelta

# Adicionar core ao path
sys.path.insert(0, '.')

from core.memory_engine import MemoryEngine
from core.risk_manager import RiskManager
from core.learning_engine import LearningEngine


def show_statistics(days: int = 30):
    """
    Exibe estatísticas de performance.
    """
    memory = MemoryEngine()
    stats = memory.get_statistics(days=days)
    
    print("═" * 60)
    print(f"📊 ESTATÍSTICAS ({days} dias)")
    print("═" * 60)
    print(f"Total Trades:     {stats['total_trades']}")
    print(f"Wins:             {stats['total_wins']}")
    print(f"Losses:           {stats['total_losses']}")
    print(f"Win Rate:         {stats['win_rate']:.2f}%")
    print(f"P&L Total:        ${stats['total_pnl']:.2f}")
    print(f"Average Win:      ${stats['average_win']:.2f}")
    print(f"Average Loss:     ${stats['average_loss']:.2f}")
    print(f"Max Win:          ${stats['max_win']:.2f}")
    print(f"Max Loss:         ${stats['max_loss']:.2f}")
    print(f"Profit Factor:    {stats['profit_factor']}")
    print("═" * 60)


def show_best_patterns():
    """
    Exibe padrões com melhor performance.
    """
    memory = MemoryEngine()
    patterns = memory.get_best_patterns(min_trades=3)
    
    print("═" * 60)
    print("✅ MELHORES PADRÕES")
    print("═" * 60)
    
    if not patterns:
        print("Nenhum padrão encontrado")
        return
    
    for i, pattern in enumerate(patterns[:10], 1):
        print(f"{i}. {pattern['pattern']}")
        print(f"   Win Rate: {pattern['win_rate']:.1f}%")
        print(f"   Trades: {pattern['total_trades']}")
        print(f"   Avg P&L: ${pattern['avg_pnl']:.2f}")
        print()


def show_worst_patterns():
    """
    Exibe padrões com pior performance.
    """
    memory = MemoryEngine()
    patterns = memory.get_worst_patterns(min_trades=3)
    
    print("═" * 60)
    print("❌ PIORES PADRÕES (EVITAR)")
    print("═" * 60)
    
    if not patterns:
        print("Nenhum padrão encontrado")
        return
    
    for i, pattern in enumerate(patterns[:10], 1):
        print(f"{i}. {pattern['pattern']}")
        print(f"   Win Rate: {pattern['win_rate']:.1f}%")
        print(f"   Trades: {pattern['total_trades']}")
        print(f"   Avg P&L: ${pattern['avg_pnl']:.2f}")
        print()


def export_trades():
    """
    Exporta trades para CSV.
    """
    memory = MemoryEngine()
    filename = f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    memory.export_to_csv(filename)
    print(f"✅ Trades exportados para {filename}")


def show_learning_summary():
    """
    Exibe resumo de insights de aprendizado.
    """
    memory = MemoryEngine()
    learning = LearningEngine(memory)
    
    print(learning.get_learning_summary())


def show_risk_status():
    """
    Exibe status de risco atual.
    """
    risk = RiskManager()
    metrics = risk.get_risk_metrics()
    
    print("═" * 60)
    print("🛡️  STATUS DE RISCO")
    print("═" * 60)
    print(f"Estado:              {metrics.risk_state}")
    print(f"Pausado:             {'SIM' if metrics.is_paused else 'NÃO'}")
    print()
    print(f"P&L Diário:          ${metrics.daily_pnl:.2f}")
    print(f"P&L Semanal:         ${metrics.weekly_pnl:.2f}")
    print(f"P&L Mensal:          ${metrics.monthly_pnl:.2f}")
    print()
    print(f"Trades Hoje:         {metrics.trades_today}")
    print(f"Losses Consecutivos: {metrics.consecutive_losses}")
    print(f"Wins Consecutivos:   {metrics.consecutive_wins}")
    print()
    print(f"Drawdown Atual:      {metrics.current_drawdown_pct:.2f}%")
    print(f"Drawdown Máximo:     {metrics.max_drawdown_pct:.2f}%")
    print()
    print(f"Win Rate:            {metrics.win_rate:.2f}%")
    print(f"Profit Factor:       {metrics.profit_factor:.2f}")
    print("═" * 60)


def main():
    """
    Interface de linha de comando.
    """
    parser = argparse.ArgumentParser(description='Utilitários do Trading Bot')
    
    parser.add_argument('command', choices=[
        'stats',
        'best-patterns',
        'worst-patterns',
        'export',
        'learning',
        'risk'
    ], help='Comando a executar')
    
    parser.add_argument('--days', type=int, default=30,
                       help='Número de dias para análise (padrão: 30)')
    
    args = parser.parse_args()
    
    if args.command == 'stats':
        show_statistics(args.days)
    
    elif args.command == 'best-patterns':
        show_best_patterns()
    
    elif args.command == 'worst-patterns':
        show_worst_patterns()
    
    elif args.command == 'export':
        export_trades()
    
    elif args.command == 'learning':
        show_learning_summary()
    
    elif args.command == 'risk':
        show_risk_status()


if __name__ == "__main__":
    main()
