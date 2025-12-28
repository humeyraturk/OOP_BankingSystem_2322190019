"""
Value Objects Module

Immutable value objects for the banking system.
Uses dataclass with frozen=True to ensure immutability.
"""

from dataclasses import dataclass
from enum import Enum


class Currency(Enum):
    """
    Enumeration of supported currencies.
    
    Attributes:
        USD: United States Dollar
        EUR: Euro
        GBP: British Pound Sterling
        TRY: Turkish Lira
    """
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    TRY = "TRY"


@dataclass(frozen=True)
class Money:
    """
    Immutable value object representing monetary amounts.
    
    This class uses frozen dataclass to ensure immutability.
    Amount is automatically rounded to 2 decimal places.
    
    Attributes:
        amount: The numerical amount
        currency: The currency type from Currency enum
    
    Examples:
        >>> usd_100 = Money(100.0, Currency.USD)
        >>> usd_50 = Money(50.0, Currency.USD)
        >>> total = usd_100 + usd_50
        >>> print(total)
        150.00 USD
    """
    amount: float
    currency: Currency
    
    def __post_init__(self):
        """Validate and round amount to 2 decimal places."""
        if not isinstance(self.amount, (int, float)):
            raise ValueError(f"Amount must be a number, got {type(self.amount)}")
        
        if not isinstance(self.currency, Currency):
            raise ValueError(f"Currency must be a Currency enum, got {type(self.currency)}")
        
        # Round to 2 decimal places
        object.__setattr__(self, 'amount', round(self.amount, 2))
    
    def __add__(self, other: 'Money') -> 'Money':
        """
        Add two Money objects. Currencies must match.
        
        Args:
            other: Another Money object
        
        Returns:
            Money: New Money object with sum
        
        Raises:
            ValueError: If currencies don't match
        """
        if not isinstance(other, Money):
            raise TypeError(f"Cannot add Money with {type(other).__name__}")
        
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: Cannot add {self.currency.value} to {other.currency.value}"
            )
        
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """
        Subtract one Money object from another. Currencies must match.
        
        Args:
            other: Money object to subtract
        
        Returns:
            Money: New Money object with difference
        
        Raises:
            ValueError: If currencies don't match
        """
        if not isinstance(other, Money):
            raise TypeError(f"Cannot subtract {type(other).__name__} from Money")
        
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: Cannot subtract {other.currency.value} from {self.currency.value}"
            )
        
        return Money(self.amount - other.amount, self.currency)
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: 'Money') -> bool:
        """Compare if less than."""
        if not isinstance(other, Money):
            raise TypeError(f"Cannot compare Money with {type(other).__name__}")
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount < other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        """Compare if greater than."""
        if not isinstance(other, Money):
            raise TypeError(f"Cannot compare Money with {type(other).__name__}")
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount > other.amount
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.amount:.2f} {self.currency.value}"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Money(amount={self.amount}, currency={self.currency})"
    
    @classmethod
    def zero(cls, currency: Currency) -> 'Money':
        """Create a Money object with zero amount."""
        return cls(0.0, currency)