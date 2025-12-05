"""
Value Objects Module

Immutable value objects for the banking system.
Uses dataclass with frozen=True to ensure immutability.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


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
    
    This class uses frozen dataclass to ensure immutability,
    which is a core requirement for financial value objects.
    
    Attributes:
        amount: The numerical amount (using float for simplicity)
        currency: The currency type from Currency enum
    
    Examples:
        >>> usd_100 = Money(100.0, Currency.USD)
        >>> usd_50 = Money(50.0, Currency.USD)
        >>> total = usd_100 + usd_50
        >>> print(total)
        Money(amount=150.0, currency=<Currency.USD: 'USD'>)
    """
    amount: float
    currency: Currency
    
    def __post_init__(self) -> None:
        """
        Validate Money object after initialization.
        
        Raises:
            ValueError: If amount or currency is invalid
        """
        if not isinstance(self.amount, (int, float)):
            raise ValueError(f"Amount must be a number, got {type(self.amount)}")
        
        if not isinstance(self.currency, Currency):
            raise ValueError(f"Currency must be a Currency enum, got {type(self.currency)}")
    
    def __add__(self, other: 'Money') -> 'Money':
        """
        Add two Money objects.
        
        Args:
            other: Another Money object to add
        
        Returns:
            New Money object with combined amount
        
        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency.value} and {other.currency.value}"
            )
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """
        Subtract one Money object from another.
        
        Args:
            other: Money object to subtract
        
        Returns:
            New Money object with the difference
        
        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract different currencies: {self.currency.value} and {other.currency.value}"
            )
        return Money(self.amount - other.amount, self.currency)
    
    def __str__(self) -> str:
        """String representation of Money."""
        return f"{self.amount:.2f} {self.currency.value}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Money(amount={self.amount}, currency={self.currency})"