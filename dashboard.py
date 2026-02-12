"""
Dashboard output helper (root-level) used by bot-core/main.py.
"""

from datetime import datetime
from typing import Optional


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.0f}%"
    except (TypeError, ValueError):
        return "-"


def _fmt_num(value: Optional[float], decimals: int = 2) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return "-"


def print_dashboard(
    symbol: str,
    tendencia_h1: str,
    pullback_m15: str,
    atr_m15: float,
    status_entrada: str,
    posicao_aberta: bool,
    trades_hoje: int,
    pnl_hoje: float,
    drawdown_dia: float,
    score: float,
    prob_buy: float,
    prob_sell: float,
    recomendacao: str,
    confianca: str,
    modo: str,
) -> None:
    """Print a concise status dashboard to stdout."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "═" * 70)
    print(f"🕒 {now} | {symbol} | MODO: {modo}")
    print("─" * 70)
    print(f"Tendência H1     : {tendencia_h1}")
    print(f"Pullback M15     : {pullback_m15}")
    print(f"ATR M15          : {_fmt_num(atr_m15, 6)}")
    print(f"Status Entrada   : {status_entrada}")
    print(f"Posição Aberta   : {'SIM' if posicao_aberta else 'NÃO'}")
    print(f"Trades Hoje      : {trades_hoje}")
    print(f"PnL Hoje         : {_fmt_num(pnl_hoje, 2)}")
    print(f"Drawdown Dia     : {_fmt_num(drawdown_dia, 2)}")
    print("─" * 70)
    print(f"Score            : {_fmt_num(score, 0)}/100")
    print(f"Prob BUY         : {_fmt_pct(prob_buy)}")
    print(f"Prob SELL        : {_fmt_pct(prob_sell)}")
    print(f"Recomendação     : {recomendacao}")
    print(f"Confiança        : {confianca}")
    print("═" * 70)
