"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ELITE VISUAL DECISION SYSTEM — EVENT CONTRACTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Standardized event schemas for institutional marker system.
This module defines the single source of truth for all 
decision events flowing from bot → backend → app.

NO PROFIT PROMISES. INSTITUTIONAL CLARITY ONLY.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from typing import Literal, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENUMS — TYPE SAFETY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MarkerType(str, Enum):
    """Visual marker categories"""
    BUY_CANDIDATE = "BUY_CANDIDATE"
    SELL_CANDIDATE = "SELL_CANDIDATE"
    NO_TRADE_ZONE = "NO_TRADE_ZONE"
    BOT_PAUSED = "BOT_PAUSED"
    HIGH_RISK_CONTEXT = "HIGH_RISK_CONTEXT"


class MarketContext(str, Enum):
    """Market regime classification"""
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    LOW_LIQUIDITY = "LOW_LIQUIDITY"
    NEWS_WINDOW = "NEWS_WINDOW"
    UNKNOWN = "UNKNOWN"


class RiskLevel(str, Enum):
    """Risk intensity"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class BotMode(str, Enum):
    """Bot operation modes"""
    HYBRID = "HYBRID"
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    SILENCE = "SILENCE"


class ExecutionStatus(str, Enum):
    """Whether marker represents execution or recommendation"""
    EXECUTED = "EXECUTED"
    RECOMMENDED = "RECOMMENDED"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRIMARY EVENT CONTRACT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class MarkerEvent:
    """
    Single standardized event for all bot decisions.
    
    This is the ONLY contract between:
    - Bot decision engine
    - Backend API
    - Flutter app (NEXUS COPILOT)
    
    Visual representation:
    - Dashed line = RECOMMENDED
    - Solid line = EXECUTED
    - Intensity varies by score/confidence
    """
    
    # Core identity
    timestamp: str
    symbol: str
    price: float
    
    # Marker classification
    marker_type: MarkerType
    execution_status: ExecutionStatus
    
    # Decision metrics
    score: float  # 0-100 quality score
    confidence: float  # 0-1 probability
    
    # Market intelligence
    market_context: MarketContext
    risk_level: RiskLevel
    
    # Bot state
    mode: BotMode
    
    # Human explanation
    reason: str
    technical_details: Optional[dict] = None
    
    # Optional execution data
    ticket: Optional[int] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict"""
        data = asdict(self)
        # Convert enums to strings
        data["marker_type"] = self.marker_type.value
        data["execution_status"] = self.execution_status.value
        data["market_context"] = self.market_context.value
        data["risk_level"] = self.risk_level.value
        data["mode"] = self.mode.value
        return data
    
    @property
    def visual_intensity(self) -> float:
        """
        Calculate visual marker intensity (0-1)
        Used for glow, opacity, line thickness
        """
        return min(1.0, self.score / 100.0 * (1.0 if self.confidence > 0.7 else 0.7))
    
    @property
    def is_actionable(self) -> bool:
        """Should trigger app notification"""
        if self.marker_type == MarkerType.NO_TRADE_ZONE:
            return False
        if self.execution_status == ExecutionStatus.EXECUTED:
            return True
        if self.score >= 75 and self.confidence >= 0.7:
            return True
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MARKET CONTEXT EVENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class MarketContextEvent:
    """
    Represents overall market regime.
    Used for subtle chart background shading.
    """
    timestamp: str
    symbol: str
    context: MarketContext
    volatility: float  # ATR-based measure
    liquidity_score: float  # 0-1
    session: str  # LONDON, NY, ASIA, OFF
    trend_strength: float  # 0-1
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data["context"] = self.context.value
        return data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT STATE EVENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class BotStateEvent:
    """
    Bot operational state change.
    Used to show pause/resume/mode changes.
    """
    timestamp: str
    mode: BotMode
    active: bool
    paused_reason: Optional[str] = None
    daily_trades: int = 0
    daily_pnl: float = 0.0
    risk_utilized: float = 0.0  # % of daily risk used
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data["mode"] = self.mode.value
        return data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACTORY FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_decision_marker(
    symbol: str,
    price: float,
    direction: Literal["BUY", "SELL"],
    score: float,
    confidence: float,
    executed: bool,
    market_context: MarketContext,
    risk_level: RiskLevel,
    mode: BotMode,
    reason: str,
    technical_details: dict = None,
    ticket: int = None,
    sl: float = None,
    tp: float = None
) -> MarkerEvent:
    """Create BUY/SELL marker event"""
    
    marker_type = MarkerType.BUY_CANDIDATE if direction == "BUY" else MarkerType.SELL_CANDIDATE
    execution_status = ExecutionStatus.EXECUTED if executed else ExecutionStatus.RECOMMENDED
    
    return MarkerEvent(
        timestamp=datetime.now().isoformat(),
        symbol=symbol,
        price=price,
        marker_type=marker_type,
        execution_status=execution_status,
        score=score,
        confidence=confidence,
        market_context=market_context,
        risk_level=risk_level,
        mode=mode,
        reason=reason,
        technical_details=technical_details,
        ticket=ticket,
        stop_loss=sl,
        take_profit=tp
    )


def create_no_trade_marker(
    symbol: str,
    price: float,
    reason: str,
    market_context: MarketContext,
    risk_level: RiskLevel,
    score: float = 0.0
) -> MarkerEvent:
    """Create NO TRADE marker — critical for user education"""
    
    return MarkerEvent(
        timestamp=datetime.now().isoformat(),
        symbol=symbol,
        price=price,
        marker_type=MarkerType.NO_TRADE_ZONE,
        execution_status=ExecutionStatus.BLOCKED,
        score=score,
        confidence=0.0,
        market_context=market_context,
        risk_level=risk_level,
        mode=BotMode.SILENCE,
        reason=reason
    )


def create_pause_marker(
    symbol: str,
    price: float,
    reason: str,
    risk_level: RiskLevel = RiskLevel.HIGH
) -> MarkerEvent:
    """Create BOT PAUSED marker"""
    
    return MarkerEvent(
        timestamp=datetime.now().isoformat(),
        symbol=symbol,
        price=price,
        marker_type=MarkerType.BOT_PAUSED,
        execution_status=ExecutionStatus.BLOCKED,
        score=0.0,
        confidence=0.0,
        market_context=MarketContext.UNKNOWN,
        risk_level=risk_level,
        mode=BotMode.SILENCE,
        reason=reason
    )


def create_high_risk_marker(
    symbol: str,
    price: float,
    reason: str,
    market_context: MarketContext
) -> MarkerEvent:
    """Create HIGH RISK warning marker"""
    
    return MarkerEvent(
        timestamp=datetime.now().isoformat(),
        symbol=symbol,
        price=price,
        marker_type=MarkerType.HIGH_RISK_CONTEXT,
        execution_status=ExecutionStatus.BLOCKED,
        score=0.0,
        confidence=0.0,
        market_context=market_context,
        risk_level=RiskLevel.EXTREME,
        mode=BotMode.SILENCE,
        reason=reason
    )
