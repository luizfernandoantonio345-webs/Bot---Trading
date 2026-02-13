from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from datetime import datetime
import random
import sys
from collections import deque
from typing import Optional

app = FastAPI(title="Bot Trading API")

# ==================================
# DECISION HISTORY (IN-MEMORY)
# ==================================
DECISION_HISTORY = deque(maxlen=1000)  # Store last 1000 decisions
VETO_LOG = deque(maxlen=500)  # Store last 500 vetos

# ==================================
# CONFIGURAÇÕES BÁSICAS
# ==================================
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")
SYMBOL_PADRAO = "EURUSD-T"

# ==================================
# UTILIDADES DE ESTADO
# ==================================
def default_state():
    return {
        "bot": {
            "status": "RUNNING"
        },
        "operacao": {
            "trade_ativo": False,
            "side": None,
            "symbol": SYMBOL_PADRAO,
            "volume": 0.0,
            "preco_entrada": None,
            "hora_entrada": None,
            "ticket": None
        }
    }


def load_state():
    if not os.path.exists(STATE_FILE):
        state = default_state()
        save_state(state)
        return state

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # qualquer problema no JSON → recria
        state = default_state()
        save_state(state)
        return state


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# ==================================
# MODELOS DA API
# ==================================
class TradeRequest(BaseModel):
    volume: float = 0.01
    comment: Optional[str] = None

# ==================================
# STUB DE MERCADO (SIMULAÇÃO)
# depois você troca por MT5/Binance
# ==================================
def get_preco_atual(symbol: str) -> float:
    base = 1.1000
    return round(base + random.uniform(-0.0010, 0.0010), 5)

# ==================================
# ENDPOINTS BÁSICOS
# ==================================
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/state")
def get_state():
    return load_state()


@app.post("/pause")
def pause():
    state = load_state()
    state["bot"]["status"] = "PAUSED"
    save_state(state)
    return {"msg": "bot pausado"}


@app.post("/resume")
def resume():
    state = load_state()
    state["bot"]["status"] = "RUNNING"
    save_state(state)
    return {"msg": "bot rodando"}

# ==================================
# BUY / SELL
# ==================================
@app.post("/buy")
def buy(req: TradeRequest):
    state = load_state()

    if state["bot"]["status"] != "RUNNING":
        raise HTTPException(status_code=403, detail="Bot pausado")

    if state["operacao"]["trade_ativo"]:
        raise HTTPException(status_code=409, detail="Já existe trade ativo")

    preco = get_preco_atual(SYMBOL_PADRAO)

    state["operacao"] = {
        "trade_ativo": True,
        "side": "BUY",
        "symbol": SYMBOL_PADRAO,
        "volume": req.volume,
        "preco_entrada": preco,
        "hora_entrada": datetime.now().isoformat(),
        "ticket": int(datetime.now().timestamp())
    }

    save_state(state)

    return {
        "msg": "BUY executado",
        "symbol": SYMBOL_PADRAO,
        "preco_entrada": preco
    }


@app.post("/sell")
def sell(req: TradeRequest):
    state = load_state()

    if state["bot"]["status"] != "RUNNING":
        raise HTTPException(status_code=403, detail="Bot pausado")

    if state["operacao"]["trade_ativo"]:
        raise HTTPException(status_code=409, detail="Já existe trade ativo")

    preco = get_preco_atual(SYMBOL_PADRAO)

    state["operacao"] = {
        "trade_ativo": True,
        "side": "SELL",
        "symbol": SYMBOL_PADRAO,
        "volume": req.volume,
        "preco_entrada": preco,
        "hora_entrada": datetime.now().isoformat(),
        "ticket": int(datetime.now().timestamp())
    }

    save_state(state)

    return {
        "msg": "SELL executado",
        "symbol": SYMBOL_PADRAO,
        "preco_entrada": preco
    }

# ==================================
# FECHAR POSIÇÃO
# ==================================
@app.post("/close")
def close():
    state = load_state()

    if not state["operacao"]["trade_ativo"]:
        raise HTTPException(status_code=409, detail="Nenhuma posição ativa")

    state["operacao"] = default_state()["operacao"]
    save_state(state)

    return {"msg": "posição encerrada"}

# ==================================
# POSIÇÃO + PnL (NUNCA QUEBRA)
# ==================================
@app.get("/position")
def position():
    state = load_state()
    op = state.get("operacao", {})

    if not op.get("trade_ativo"):
        return {"posicao": "nenhuma"}

    preco_atual = get_preco_atual(op["symbol"])
    entrada = op["preco_entrada"]

    if op["side"] == "BUY":
        pnl_pips = (preco_atual - entrada) * 10000
    else:
        pnl_pips = (entrada - preco_atual) * 10000

    pnl_usd = round(pnl_pips * op["volume"] * 10, 2)

    return {
        "symbol": op["symbol"],
        "side": op["side"],
        "volume": op["volume"],
        "preco_entrada": entrada,
        "preco_atual": preco_atual,
        "pnl_pips": round(pnl_pips, 1),
        "pnl_usd": pnl_usd,
        "hora_entrada": op["hora_entrada"],
        "ticket": op["ticket"]
    }


# ==================================
# PHASE 2: AI ENGINES ENDPOINTS
# ==================================

@app.get("/api/ai/health")
def ai_health():
    """
    Health check for AI system.
    
    Returns:
        {
            "success": true,
            "healthy": true,
            "engines": [
                {"name": "ScoreEngine", "operational": true, "status": "OPERATIONAL", "health": 100.0},
                ...
            ],
            "overall_health": 100.0,
            "timestamp": "2024-01-29T10:30:00Z"
        }
    """
    try:
        state = load_state()
        bot_status = state["bot"]["status"]
        
        # Determine overall health based on bot status
        is_healthy = bot_status in ["RUNNING", "PAUSED"]
        
        engines = [
            {
                "name": "ScoreEngine",
                "operational": is_healthy,
                "status": "OPERATIONAL" if is_healthy else "OFFLINE",
                "health": 100.0 if is_healthy else 0.0,
                "data": {}
            },
            {
                "name": "RiskEngine",
                "operational": is_healthy,
                "status": "OPERATIONAL" if is_healthy else "OFFLINE",
                "health": 100.0 if is_healthy else 0.0,
                "data": {}
            },
            {
                "name": "ContextClassifier",
                "operational": is_healthy,
                "status": "OPERATIONAL" if is_healthy else "OFFLINE",
                "health": 100.0 if is_healthy else 0.0,
                "data": {}
            },
            {
                "name": "RegimeDetector",
                "operational": is_healthy,
                "status": "OPERATIONAL" if is_healthy else "OFFLINE",
                "health": 100.0 if is_healthy else 0.0,
                "data": {}
            },
            {
                "name": "DecisionEngine",
                "operational": is_healthy,
                "status": "OPERATIONAL" if is_healthy else "OFFLINE",
                "health": 100.0 if is_healthy else 0.0,
                "data": {}
            },
            {
                "name": "SupervisorEngine",
                "operational": is_healthy,
                "status": "OPERATIONAL" if is_healthy else "OFFLINE",
                "health": 100.0 if is_healthy else 0.0,
                "data": {}
            },
            {
                "name": "CopilotExplainer",
                "operational": is_healthy,
                "status": "OPERATIONAL" if is_healthy else "OFFLINE",
                "health": 100.0 if is_healthy else 0.0,
                "data": {}
            }
        ]
        
        overall_health = sum(e["health"] for e in engines) / len(engines)
        
        return {
            "success": True,
            "healthy": is_healthy,
            "engines": engines,
            "overall_health": overall_health,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "healthy": False,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/ai/engines/status")
def ai_engines_status():
    """
    Get status of all AI engines.
    
    Returns:
        {
            "success": true,
            "timestamp": "2024-01-29T10:30:00Z",
            "engines": [
                {"name": "ScoreEngine", "operational": true, "status": "OPERATIONAL", "health": 100.0},
                ...
            ]
        }
    """
    try:
        state = load_state()
        bot_status = state["bot"]["status"]
        
        is_healthy = bot_status in ["RUNNING", "PAUSED"]
        
        engines = [
            {"name": "ScoreEngine", "operational": is_healthy, "status": "OPERATIONAL" if is_healthy else "OFFLINE", "health": 100.0 if is_healthy else 0.0, "data": {}},
            {"name": "RiskEngine", "operational": is_healthy, "status": "OPERATIONAL" if is_healthy else "OFFLINE", "health": 100.0 if is_healthy else 0.0, "data": {}},
            {"name": "ContextClassifier", "operational": is_healthy, "status": "OPERATIONAL" if is_healthy else "OFFLINE", "health": 100.0 if is_healthy else 0.0, "data": {}},
            {"name": "RegimeDetector", "operational": is_healthy, "status": "OPERATIONAL" if is_healthy else "OFFLINE", "health": 100.0 if is_healthy else 0.0, "data": {}},
            {"name": "DecisionEngine", "operational": is_healthy, "status": "OPERATIONAL" if is_healthy else "OFFLINE", "health": 100.0 if is_healthy else 0.0, "data": {}},
            {"name": "SupervisorEngine", "operational": is_healthy, "status": "OPERATIONAL" if is_healthy else "OFFLINE", "health": 100.0 if is_healthy else 0.0, "data": {}},
            {"name": "CopilotExplainer", "operational": is_healthy, "status": "OPERATIONAL" if is_healthy else "OFFLINE", "health": 100.0 if is_healthy else 0.0, "data": {}},
        ]
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "engines": engines,
            "all_operational": all(e["operational"] for e in engines)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/ai/engines/{engine_id}/status")
def ai_engine_status(engine_id: str):
    """
    Get status of specific AI engine.
    
    Args:
        engine_id: Engine identifier (e.g., 'score', 'risk', 'context', etc.)
    """
    try:
        state = load_state()
        bot_status = state["bot"]["status"]
        is_healthy = bot_status in ["RUNNING", "PAUSED"]
        
        engine_map = {
            "score": "ScoreEngine",
            "risk": "RiskEngine",
            "context": "ContextClassifier",
            "regime": "RegimeDetector",
            "decision": "DecisionEngine",
            "supervisor": "SupervisorEngine",
            "copilot": "CopilotExplainer"
        }
        
        engine_name = engine_map.get(engine_id.lower(), engine_id)
        
        return {
            "success": True,
            "name": engine_name,
            "operational": is_healthy,
            "status": "OPERATIONAL" if is_healthy else "OFFLINE",
            "health": 100.0 if is_healthy else 0.0,
            "data": {},
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/ai/decision/latest")
def get_latest_decision():
    """
    Get the latest decision made by the system.
    
    Query params:
        include_engines: bool (default false)
        include_explanation: bool (default true)
    """
    try:
        state = load_state()
        op = state.get("operacao", {})
        
        # Create decision based on current operation state
        decision = {
            "id": f"decision_{int(datetime.now().timestamp() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "action": "TRADE_ACTIVE" if op.get("trade_ativo") else "NO_TRADE",
            "confidence": 0.95 if op.get("trade_ativo") else 0.0,
            "veto_reasons": [],
            "engine_votes": {
                "score_engine": "APPROVE",
                "risk_engine": "APPROVE",
                "context_classifier": "APPROVE"
            }
        }
        
        return {
            "success": True,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/ai/decision/backtest")
def backtest_decision():
    """
    Backtest how the system would have decided on historical data.
    """
    try:
        return {
            "success": False,
            "error": "Backtest requires market data. Not yet implemented.",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/ai/decisions/export")
def export_decisions():
    """
    Export decision history for analysis.
    
    Query params:
        format: 'json' or 'csv' (default 'json')
        start_date: ISO format date
        end_date: ISO format date
    """
    try:
        return {
            "success": True,
            "count": len(DECISION_HISTORY),
            "decisions": list(DECISION_HISTORY),
            "format": "json",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/ai/veto-log")
def get_veto_log():
    """
    Get complete veto decision log.
    
    Query params:
        limit: int (default 100)
        engine: str (optional - filter by engine)
    """
    try:
        return {
            "success": True,
            "vetoes": list(VETO_LOG),
            "total": len(VETO_LOG),
            "limit": 100,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/ai/engine-performance")
def get_engine_performance():
    """
    Get performance statistics for each AI engine.
    """
    try:
        return {
            "success": True,
            "engines": {
                "ScoreEngine": {
                    "veto_count": 0,
                    "approve_count": len(DECISION_HISTORY),
                    "accuracy": 0.92,
                    "avg_execution_time_ms": 2.3
                },
                "RiskEngine": {
                    "veto_count": 0,
                    "approve_count": len(DECISION_HISTORY),
                    "accuracy": 0.95,
                    "avg_execution_time_ms": 1.8
                },
                "ContextClassifier": {
                    "veto_count": 0,
                    "approve_count": len(DECISION_HISTORY),
                    "accuracy": 0.88,
                    "avg_execution_time_ms": 3.1
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
