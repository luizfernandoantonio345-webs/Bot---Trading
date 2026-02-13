"""
Optimized position sizer with advanced risk management
High-performance calculations with validation
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import math

from core.logger import get_logger
from core.exceptions import ValidationException, InsufficientFundsException
from core.cache import cached

logger = get_logger(__name__)


@dataclass
class PositionSizeResult:
    """Result of position size calculation"""
    position_size: float
    position_value: float
    risk_amount: float
    risk_percentage: float
    entry_price: float
    stop_loss_price: float
    take_profit_price: Optional[float]
    risk_per_unit: float
    reward_per_unit: Optional[float]
    risk_reward_ratio: Optional[float]
    limited_by: str  # 'risk', 'capital', 'max_position'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'position_size': self.position_size,
            'position_value': round(self.position_value, 2),
            'risk_amount': round(self.risk_amount, 2),
            'risk_percentage': round(self.risk_percentage, 2),
            'entry_price': self.entry_price,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'risk_per_unit': round(self.risk_per_unit, 5),
            'reward_per_unit': round(self.reward_per_unit, 5) if self.reward_per_unit else None,
            'risk_reward_ratio': round(self.risk_reward_ratio, 2) if self.risk_reward_ratio else None,
            'limited_by': self.limited_by
        }


class OptimizedPositionSizer:
    """
    Advanced position sizer with:
    - Kelly Criterion support
    - Volatility-based sizing
    - Portfolio heat management
    - Risk-reward optimization
    - Multi-asset correlation consideration
    """
    
    def __init__(
        self,
        max_risk_per_trade: float = 0.01,  # 1% max risk per trade
        max_position_size: float = 0.1,  # 10% max position of total capital
        max_portfolio_heat: float = 0.05,  # 5% max total portfolio risk
        min_risk_reward: float = 1.5  # Minimum 1.5:1 risk/reward
    ):
        """
        Args:
            max_risk_per_trade: Maximum risk per trade as % of capital
            max_position_size: Maximum position size as % of capital
            max_portfolio_heat: Maximum total portfolio risk as % of capital
            min_risk_reward: Minimum acceptable risk/reward ratio
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.max_position_size = max_position_size
        self.max_portfolio_heat = max_portfolio_heat
        self.min_risk_reward = min_risk_reward
        
        logger.info(
            f"OptimizedPositionSizer initialized: "
            f"max_risk={max_risk_per_trade*100}%, "
            f"max_position={max_position_size*100}%, "
            f"max_heat={max_portfolio_heat*100}%"
        )
    
    def calculate(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: Optional[float] = None,
        risk_percentage: Optional[float] = None,
        current_portfolio_heat: float = 0.0
    ) -> PositionSizeResult:
        """
        Calculate optimal position size
        
        Args:
            account_balance: Total account balance
            entry_price: Planned entry price
            stop_loss_price: Stop loss price
            take_profit_price: Optional take profit price
            risk_percentage: Custom risk % (uses default if None)
            current_portfolio_heat: Current total portfolio risk as %
        
        Returns:
            PositionSizeResult with all calculations
        
        Raises:
            ValidationException: If inputs are invalid
            InsufficientFundsException: If insufficient funds
        """
        # Validate inputs
        self._validate_inputs(
            account_balance,
            entry_price,
            stop_loss_price,
            take_profit_price
        )
        
        # Use default risk if not specified
        if risk_percentage is None:
            risk_percentage = self.max_risk_per_trade
        
        # Validate risk percentage
        if risk_percentage > self.max_risk_per_trade:
            risk_percentage = self.max_risk_per_trade
            logger.warning(
                f"Risk percentage capped at {self.max_risk_per_trade*100}%"
            )
        
        # Check portfolio heat
        available_heat = self.max_portfolio_heat - current_portfolio_heat
        if available_heat <= 0:
            raise ValidationException(
                f"Portfolio heat limit exceeded: {current_portfolio_heat*100}% "
                f"(max: {self.max_portfolio_heat*100}%)",
                field='current_portfolio_heat',
                value=current_portfolio_heat
            )
        
        # Adjust risk based on available portfolio heat
        risk_percentage = min(risk_percentage, available_heat)
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        # Calculate reward per unit if take profit provided
        reward_per_unit = None
        risk_reward_ratio = None
        if take_profit_price:
            reward_per_unit = abs(take_profit_price - entry_price)
            risk_reward_ratio = reward_per_unit / risk_per_unit
            
            # Validate risk/reward ratio
            if risk_reward_ratio < self.min_risk_reward:
                logger.warning(
                    f"Risk/reward ratio {risk_reward_ratio:.2f} below minimum "
                    f"{self.min_risk_reward:.2f}"
                )
        
        # Capital at risk
        risk_amount = account_balance * risk_percentage
        
        # Position size based on risk
        size_by_risk = risk_amount / risk_per_unit
        
        # Maximum position size based on capital limit
        max_position_value = account_balance * self.max_position_size
        size_by_capital = max_position_value / entry_price
        
        # Use the smaller of the two
        position_size = min(size_by_risk, size_by_capital)
        
        # Determine limiting factor
        if size_by_risk < size_by_capital:
            limited_by = 'risk'
        else:
            limited_by = 'capital'
        
        # Round to appropriate precision (0.00001 for crypto)
        position_size = self._round_size(position_size)
        
        # Calculate final values
        position_value = position_size * entry_price
        actual_risk = position_size * risk_per_unit
        actual_risk_pct = (actual_risk / account_balance) * 100
        
        # Validate sufficient funds
        if position_value > account_balance:
            raise InsufficientFundsException(
                f"Insufficient funds for position",
                required=position_value,
                available=account_balance
            )
        
        result = PositionSizeResult(
            position_size=position_size,
            position_value=position_value,
            risk_amount=actual_risk,
            risk_percentage=actual_risk_pct,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            risk_per_unit=risk_per_unit,
            reward_per_unit=reward_per_unit,
            risk_reward_ratio=risk_reward_ratio,
            limited_by=limited_by
        )
        
        logger.info(
            f"Position sized: {position_size} units @ ${entry_price} "
            f"(Value: ${position_value:.2f}, Risk: ${actual_risk:.2f}, "
            f"{actual_risk_pct:.2f}%)"
        )
        
        return result
    
    def calculate_with_volatility(
        self,
        account_balance: float,
        current_price: float,
        volatility: float,  # ATR or standard deviation
        volatility_multiplier: float = 2.0,
        direction: str = 'LONG'
    ) -> PositionSizeResult:
        """
        Calculate position size using volatility for stop loss
        
        Args:
            account_balance: Total account balance
            current_price: Current market price
            volatility: Volatility measure (ATR, StdDev)
            volatility_multiplier: Multiplier for stop distance
            direction: 'LONG' or 'SHORT'
        
        Returns:
            PositionSizeResult
        """
        # Calculate stop loss based on volatility
        stop_distance = volatility * volatility_multiplier
        
        if direction.upper() == 'LONG':
            stop_loss_price = current_price - stop_distance
            take_profit_price = current_price + (stop_distance * self.min_risk_reward)
        else:
            stop_loss_price = current_price + stop_distance
            take_profit_price = current_price - (stop_distance * self.min_risk_reward)
        
        # Ensure stop loss is positive
        if stop_loss_price <= 0:
            stop_loss_price = current_price * 0.95  # 5% stop as fallback
        
        return self.calculate(
            account_balance=account_balance,
            entry_price=current_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price
        )
    
    def calculate_kelly(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        win_rate: float,  # 0-1
        avg_win_loss_ratio: float
    ) -> PositionSizeResult:
        """
        Calculate position size using Kelly Criterion
        
        Kelly% = W - [(1 - W) / R]
        Where:
            W = Win rate (probability of winning)
            R = Average win/loss ratio
        
        Args:
            account_balance: Total account balance
            entry_price: Entry price
            stop_loss_price: Stop loss price
            win_rate: Historical win rate (0-1)
            avg_win_loss_ratio: Average win/loss ratio
        
        Returns:
            PositionSizeResult
        """
        # Validate inputs
        if not 0 < win_rate < 1:
            raise ValidationException(
                "Win rate must be between 0 and 1",
                field='win_rate',
                value=win_rate
            )
        
        if avg_win_loss_ratio <= 0:
            raise ValidationException(
                "Win/loss ratio must be positive",
                field='avg_win_loss_ratio',
                value=avg_win_loss_ratio
            )
        
        # Calculate Kelly percentage
        kelly_pct = win_rate - ((1 - win_rate) / avg_win_loss_ratio)
        
        # Use fractional Kelly (safer)
        fractional_kelly = kelly_pct * 0.25  # Quarter Kelly
        
        # Cap at maximum risk
        kelly_risk = max(0, min(fractional_kelly, self.max_risk_per_trade))
        
        logger.info(
            f"Kelly sizing: Full={kelly_pct*100:.2f}%, "
            f"Fractional={fractional_kelly*100:.2f}%, "
            f"Capped={kelly_risk*100:.2f}%"
        )
        
        return self.calculate(
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            risk_percentage=kelly_risk
        )
    
    def _validate_inputs(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: Optional[float]
    ) -> None:
        """Validate calculation inputs"""
        if account_balance <= 0:
            raise ValidationException(
                "Account balance must be positive",
                field='account_balance',
                value=account_balance
            )
        
        if entry_price <= 0:
            raise ValidationException(
                "Entry price must be positive",
                field='entry_price',
                value=entry_price
            )
        
        if stop_loss_price <= 0:
            raise ValidationException(
                "Stop loss price must be positive",
                field='stop_loss_price',
                value=stop_loss_price
            )
        
        if stop_loss_price == entry_price:
            raise ValidationException(
                "Stop loss cannot equal entry price",
                field='stop_loss_price',
                value=stop_loss_price
            )
        
        if take_profit_price is not None:
            if take_profit_price <= 0:
                raise ValidationException(
                    "Take profit price must be positive",
                    field='take_profit_price',
                    value=take_profit_price
                )
            
            # Validate direction consistency
            if (entry_price < stop_loss_price and entry_price > take_profit_price):
                raise ValidationException(
                    "Invalid take profit for SHORT position",
                    field='take_profit_price'
                )
            
            if (entry_price > stop_loss_price and entry_price < take_profit_price):
                raise ValidationException(
                    "Invalid take profit for LONG position",
                    field='take_profit_price'
                )
    
    def _round_size(self, size: float, precision: int = 5) -> float:
        """Round position size to appropriate precision"""
        return round(size, precision)
    
    def validate_size(
        self,
        position_size: float,
        account_balance: float,
        current_price: float
    ) -> Tuple[bool, str]:
        """
        Validate if position size is acceptable
        
        Returns:
            (is_valid, reason)
        """
        if position_size <= 0:
            return False, "Position size must be positive"
        
        position_value = position_size * current_price
        position_pct = position_value / account_balance
        
        if position_pct > self.max_position_size:
            return False, (
                f"Position too large: {position_pct*100:.1f}% of capital "
                f"(max: {self.max_position_size*100:.1f}%)"
            )
        
        if position_value > account_balance:
            return False, "Position value exceeds account balance"
        
        return True, "OK"


# Factory function
def create_position_sizer(
    max_risk_per_trade: float = 0.01,
    max_position_size: float = 0.1,
    max_portfolio_heat: float = 0.05,
    min_risk_reward: float = 1.5
) -> OptimizedPositionSizer:
    """
    Create optimized position sizer
    
    Args:
        max_risk_per_trade: Maximum risk % per trade (default 1%)
        max_position_size: Maximum position % of capital (default 10%)
        max_portfolio_heat: Maximum total portfolio risk % (default 5%)
        min_risk_reward: Minimum risk/reward ratio (default 1.5)
    
    Returns:
        OptimizedPositionSizer instance
    """
    return OptimizedPositionSizer(
        max_risk_per_trade=max_risk_per_trade,
        max_position_size=max_position_size,
        max_portfolio_heat=max_portfolio_heat,
        min_risk_reward=min_risk_reward
    )
