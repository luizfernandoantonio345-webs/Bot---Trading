"""
Dynamic Position Sizing
Calcula tamanho ideal de posição baseado em risco e volatilidade
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Calcula tamanho de posição baseado em:
    - Saldo da conta
    - Percentual de risco
    - Volatilidade do ativo
    - Stop loss
    """
    
    def __init__(
        self,
        max_risk_per_trade: float = 0.01,  # 1% máximo por trade
        max_position_size: float = 0.1      # 10% do capital máximo em uma posição
    ):
        """
        Args:
            max_risk_per_trade: % máximo do capital em risco por trade
            max_position_size: % máximo do capital em uma posição
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.max_position_size = max_position_size
        
    def calculate_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        risk_percentage: Optional[float] = None
    ) -> dict:
        """
        Calcula tamanho ideal da posição
        
        Args:
            account_balance: Saldo da conta
            entry_price: Preço de entrada
            stop_loss_price: Preço do stop loss
            risk_percentage: % de risco (opcional, usa default se None)
            
        Returns:
            dict com tamanho e informações
        """
        if risk_percentage is None:
            risk_percentage = self.max_risk_per_trade
        
        # Validações
        if account_balance <= 0:
            raise ValueError("Saldo da conta deve ser positivo")
        
        if entry_price <= 0 or stop_loss_price <= 0:
            raise ValueError("Preços devem ser positivos")
        
        # Calcular risco por unidade
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit == 0:
            raise ValueError("Stop loss não pode ser igual ao preço de entrada")
        
        # Capital em risco
        risk_amount = account_balance * risk_percentage
        
        # Tamanho baseado em risco
        size_by_risk = risk_amount / risk_per_unit
        
        # Tamanho máximo baseado em % do capital
        max_size_by_capital = (account_balance * self.max_position_size) / entry_price
        
        # Usar o menor dos dois
        position_size = min(size_by_risk, max_size_by_capital)
        
        # Arredondar para precisão apropriada (5 casas decimais para crypto)
        position_size = round(position_size, 5)
        
        # Calcular valores
        position_value = position_size * entry_price
        actual_risk = position_size * risk_per_unit
        risk_pct = (actual_risk / account_balance) * 100
        
        result = {
            'position_size': position_size,
            'position_value': round(position_value, 2),
            'risk_amount': round(actual_risk, 2),
            'risk_percentage': round(risk_pct, 2),
            'entry_price': entry_price,
            'stop_loss_price': stop_loss_price,
            'risk_per_unit': round(risk_per_unit, 5),
            'limited_by': 'risk' if size_by_risk < max_size_by_capital else 'capital'
        }
        
        logger.info(
            f"Position size calculado: {position_size} "
            f"(Valor: ${position_value:.2f}, Risco: ${actual_risk:.2f}, {risk_pct:.2f}%)"
        )
        
        return result
    
    def calculate_with_volatility(
        self,
        account_balance: float,
        current_price: float,
        volatility: float,  # ATR ou desvio padrão
        volatility_multiplier: float = 2.0
    ) -> dict:
        """
        Calcula posição usando volatilidade para determinar stop loss
        
        Args:
            account_balance: Saldo da conta
            current_price: Preço atual
            volatility: Medida de volatilidade (ATR, StdDev)
            volatility_multiplier: Multiplicador da volatilidade para stop
            
        Returns:
            dict com tamanho e informações
        """
        # Stop loss baseado em volatilidade
        stop_distance = volatility * volatility_multiplier
        stop_loss_price = current_price - stop_distance
        
        if stop_loss_price <= 0:
            # Ajustar se stop loss ficar negativo
            stop_loss_price = current_price * 0.95  # 5% abaixo
        
        result = self.calculate_size(
            account_balance=account_balance,
            entry_price=current_price,
            stop_loss_price=stop_loss_price
        )
        
        result['volatility'] = round(volatility, 5)
        result['volatility_multiplier'] = volatility_multiplier
        result['stop_distance'] = round(stop_distance, 5)
        
        return result
    
    def validate_size(
        self,
        position_size: float,
        account_balance: float,
        current_price: float
    ) -> tuple[bool, str]:
        """
        Valida se um tamanho de posição é aceitável
        
        Returns:
            (is_valid, reason)
        """
        if position_size <= 0:
            return False, "Tamanho de posição deve ser positivo"
        
        position_value = position_size * current_price
        position_pct = position_value / account_balance
        
        if position_pct > self.max_position_size:
            return False, f"Posição muito grande: {position_pct*100:.1f}% do capital (máx: {self.max_position_size*100:.1f}%)"
        
        if position_value > account_balance:
            return False, "Posição maior que o saldo da conta"
        
        return True, "OK"


# Instância global
position_sizer = PositionSizer(
    max_risk_per_trade=0.01,  # 1% de risco
    max_position_size=0.05     # 5% do capital máximo por posição
)
