"""
═══════════════════════════════════════════════════════════════════
MEMORY ENGINE - ARMAZENAMENTO PERSISTENTE DE TRADES
═══════════════════════════════════════════════════════════════════
Armazena todos os trades com contexto completo para análise e aprendizado.
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class TradeRecord:
    """Registro completo de um trade."""
    trade_id: str
    timestamp: str
    symbol: str
    side: str  # BUY/SELL ou LONG/SHORT
    
    # Execução
    entry_price: float
    exit_price: float
    quantity: float
    
    # Resultado
    pnl: float
    pnl_percent: float
    was_win: bool
    
    # Stop/Target
    stop_loss: Optional[float]
    take_profit: Optional[float]
    exit_reason: str  # "STOP_LOSS", "TAKE_PROFIT", "MANUAL", "TIME"
    
    # Contexto de mercado no momento
    market_trend: str
    market_structure: str
    volatility_level: str
    session: str
    
    # Score e decisão
    score: int
    confidence: float
    primary_pattern: Optional[str]
    
    # Métricas de risco
    risk_amount: float
    reward_amount: float
    risk_reward_ratio: float
    
    # Performance
    duration_seconds: int
    slippage: float
    
    # Tags e notas
    tags: List[str]
    notes: str


class MemoryEngine:
    """
    Motor de memória persistente para armazenamento de trades.
    Usa SQLite para performance e facilidade.
    """
    
    def __init__(self, db_path: str = "trade_memory.db"):
        """
        Inicializa motor de memória.
        
        Args:
            db_path: Caminho do banco de dados SQLite
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """
        Inicializa estrutura do banco de dados.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                quantity REAL NOT NULL,
                
                pnl REAL NOT NULL,
                pnl_percent REAL NOT NULL,
                was_win INTEGER NOT NULL,
                
                stop_loss REAL,
                take_profit REAL,
                exit_reason TEXT,
                
                market_trend TEXT,
                market_structure TEXT,
                volatility_level TEXT,
                session TEXT,
                
                score INTEGER,
                confidence REAL,
                primary_pattern TEXT,
                
                risk_amount REAL,
                reward_amount REAL,
                risk_reward_ratio REAL,
                
                duration_seconds INTEGER,
                slippage REAL,
                
                tags TEXT,
                notes TEXT
            )
        ''')
        
        # Índices para queries rápidas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON trades(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON trades(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_was_win ON trades(was_win)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_exit_reason ON trades(exit_reason)')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Memory Engine inicializado | DB: {self.db_path}")
    
    def save_trade(self, trade: TradeRecord):
        """
        Salva trade no banco de dados.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Converter tags para JSON
        tags_json = json.dumps(trade.tags)
        
        cursor.execute('''
            INSERT OR REPLACE INTO trades VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            trade.trade_id,
            trade.timestamp,
            trade.symbol,
            trade.side,
            trade.entry_price,
            trade.exit_price,
            trade.quantity,
            trade.pnl,
            trade.pnl_percent,
            1 if trade.was_win else 0,
            trade.stop_loss,
            trade.take_profit,
            trade.exit_reason,
            trade.market_trend,
            trade.market_structure,
            trade.volatility_level,
            trade.session,
            trade.score,
            trade.confidence,
            trade.primary_pattern,
            trade.risk_amount,
            trade.reward_amount,
            trade.risk_reward_ratio,
            trade.duration_seconds,
            trade.slippage,
            tags_json,
            trade.notes
        ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Trade salvo | ID: {trade.trade_id} | P&L: ${trade.pnl:.2f}")
    
    def get_trade(self, trade_id: str) -> Optional[TradeRecord]:
        """
        Recupera trade específico.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trades WHERE trade_id = ?', (trade_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return self._row_to_trade(row)
        return None
    
    def get_all_trades(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        wins_only: bool = False,
        losses_only: bool = False
    ) -> List[TradeRecord]:
        """
        Recupera trades com filtros.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM trades WHERE 1=1'
        params = []
        
        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        if wins_only:
            query += ' AND was_win = 1'
        
        if losses_only:
            query += ' AND was_win = 0'
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return [self._row_to_trade(row) for row in rows]
    
    def get_statistics(self, days: int = 30) -> Dict:
        """
        Calcula estatísticas dos últimos N dias.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Data de início
        start_date = (datetime.now() - pd.Timedelta(days=days)).isoformat()
        
        # Total trades
        cursor.execute(
            'SELECT COUNT(*) FROM trades WHERE timestamp >= ?',
            (start_date,)
        )
        total_trades = cursor.fetchone()[0]
        
        # Wins e losses
        cursor.execute(
            'SELECT COUNT(*) FROM trades WHERE timestamp >= ? AND was_win = 1',
            (start_date,)
        )
        total_wins = cursor.fetchone()[0]
        
        cursor.execute(
            'SELECT COUNT(*) FROM trades WHERE timestamp >= ? AND was_win = 0',
            (start_date,)
        )
        total_losses = cursor.fetchone()[0]
        
        # P&L total
        cursor.execute(
            'SELECT SUM(pnl) FROM trades WHERE timestamp >= ?',
            (start_date,)
        )
        total_pnl = cursor.fetchone()[0] or 0.0
        
        # P&L médio wins
        cursor.execute(
            'SELECT AVG(pnl) FROM trades WHERE timestamp >= ? AND was_win = 1',
            (start_date,)
        )
        avg_win = cursor.fetchone()[0] or 0.0
        
        # P&L médio losses
        cursor.execute(
            'SELECT AVG(pnl) FROM trades WHERE timestamp >= ? AND was_win = 0',
            (start_date,)
        )
        avg_loss = cursor.fetchone()[0] or 0.0
        
        # Maior win
        cursor.execute(
            'SELECT MAX(pnl) FROM trades WHERE timestamp >= ? AND was_win = 1',
            (start_date,)
        )
        max_win = cursor.fetchone()[0] or 0.0
        
        # Maior loss
        cursor.execute(
            'SELECT MIN(pnl) FROM trades WHERE timestamp >= ? AND was_win = 0',
            (start_date,)
        )
        max_loss = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        # Calcular métricas derivadas
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0.0
        
        if abs(avg_loss) > 0:
            profit_factor = abs(avg_win * total_wins) / abs(avg_loss * total_losses)
        else:
            profit_factor = float('inf') if total_wins > 0 else 0.0
        
        return {
            "period_days": days,
            "total_trades": total_trades,
            "total_wins": total_wins,
            "total_losses": total_losses,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "max_win": round(max_win, 2),
            "max_loss": round(max_loss, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "∞"
        }
    
    def get_pattern_performance(self, pattern: str) -> Dict:
        """
        Analisa performance de um padrão específico.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total trades com esse padrão
        cursor.execute(
            'SELECT COUNT(*) FROM trades WHERE primary_pattern = ?',
            (pattern,)
        )
        total = cursor.fetchone()[0]
        
        if total == 0:
            conn.close()
            return {
                "pattern": pattern,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_pnl": 0.0
            }
        
        # Wins
        cursor.execute(
            'SELECT COUNT(*) FROM trades WHERE primary_pattern = ? AND was_win = 1',
            (pattern,)
        )
        wins = cursor.fetchone()[0]
        
        # P&L médio
        cursor.execute(
            'SELECT AVG(pnl) FROM trades WHERE primary_pattern = ?',
            (pattern,)
        )
        avg_pnl = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        win_rate = (wins / total * 100) if total > 0 else 0.0
        
        return {
            "pattern": pattern,
            "total_trades": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": round(win_rate, 2),
            "avg_pnl": round(avg_pnl, 2)
        }
    
    def get_best_patterns(self, min_trades: int = 5) -> List[Dict]:
        """
        Retorna padrões com melhor performance.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                primary_pattern,
                COUNT(*) as total,
                SUM(CASE WHEN was_win = 1 THEN 1 ELSE 0 END) as wins,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE primary_pattern IS NOT NULL
            GROUP BY primary_pattern
            HAVING COUNT(*) >= ?
            ORDER BY avg_pnl DESC
        ''', (min_trades,))
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            pattern, total, wins, avg_pnl = row
            win_rate = (wins / total * 100) if total > 0 else 0.0
            
            patterns.append({
                "pattern": pattern,
                "total_trades": total,
                "wins": wins,
                "win_rate": round(win_rate, 2),
                "avg_pnl": round(avg_pnl, 2)
            })
        
        return patterns
    
    def get_worst_patterns(self, min_trades: int = 5) -> List[Dict]:
        """
        Retorna padrões com pior performance.
        """
        best = self.get_best_patterns(min_trades)
        return list(reversed(best))
    
    def export_to_csv(self, filename: str = "trades_export.csv"):
        """
        Exporta todos os trades para CSV.
        """
        trades = self.get_all_trades()
        
        if not trades:
            print("⚠️  Nenhum trade para exportar")
            return
        
        # Converter para DataFrame
        data = [asdict(trade) for trade in trades]
        df = pd.DataFrame(data)
        
        # Salvar
        df.to_csv(filename, index=False)
        print(f"✅ {len(trades)} trades exportados para {filename}")
    
    def _row_to_trade(self, row) -> TradeRecord:
        """
        Converte row do banco para TradeRecord.
        """
        tags = json.loads(row[25]) if row[25] else []
        
        return TradeRecord(
            trade_id=row[0],
            timestamp=row[1],
            symbol=row[2],
            side=row[3],
            entry_price=row[4],
            exit_price=row[5],
            quantity=row[6],
            pnl=row[7],
            pnl_percent=row[8],
            was_win=bool(row[9]),
            stop_loss=row[10],
            take_profit=row[11],
            exit_reason=row[12],
            market_trend=row[13],
            market_structure=row[14],
            volatility_level=row[15],
            session=row[16],
            score=row[17],
            confidence=row[18],
            primary_pattern=row[19],
            risk_amount=row[20],
            reward_amount=row[21],
            risk_reward_ratio=row[22],
            duration_seconds=row[23],
            slippage=row[24],
            tags=tags,
            notes=row[26] or ""
        )


if __name__ == "__main__":
    print("Memory Engine - Armazenamento Persistente de Trades")
    print("Módulo pronto para integração")
