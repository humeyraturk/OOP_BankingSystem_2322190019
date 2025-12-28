"""
Savings Account Module

Savings account with interest calculation and application.
"""

from datetime import datetime
import uuid
from .account import Account
from .value_objects import Money
from .transaction import Transaction, TransactionType


class SavingsAccount(Account):
    """
    Savings account with interest earning capability.
    
    This account type earns interest on the balance. Interest can be
    applied periodically and is recorded as a transaction.
    
    Attributes:
        interest_rate: Annual interest rate (e.g., 0.05 for 5%)
    
    Examples:
        >>> account = SavingsAccount(
        ...     "ACC001",
        ...     "CUST001",
        ...     Money(1000.0, Currency.USD),
        ...     interest_rate=0.05
        ... )
        >>> interest = account.apply_interest()
        >>> print(f"Interest earned: {interest}")
        Interest earned: 50.00 USD
    """
    
    def __init__(
        self,
        account_number: str,
        owner_id: str,
        initial_balance: Money,
        interest_rate: float = 0.05
    ):
        """
        Initialize a savings account.
        
        Args:
            account_number: Unique account identifier
            owner_id: Customer ID
            initial_balance: Starting balance
            interest_rate: Annual interest rate (default: 0.05 = 5%)
        
        Raises:
            ValueError: If interest rate is negative
        """
        super().__init__(account_number, owner_id, initial_balance)
        
        if interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        
        self._interest_rate: float = interest_rate
    
    @property
    def interest_rate(self) -> float:
        """Get the annual interest rate."""
        return self._interest_rate
    
    @interest_rate.setter
    def interest_rate(self, value: float) -> None:
        """
        Set the annual interest rate.
        
        Args:
            value: New interest rate
        
        Raises:
            ValueError: If rate is negative
        """
        if value < 0:
            raise ValueError("Interest rate cannot be negative")
        self._interest_rate = value
    
    def calculate_interest(self) -> Money:
        """
        Calculate interest on current balance.
        
        Uses simple interest formula: Interest = Principal × Rate
        
        Returns:
            Money: Interest amount to be earned
        
        Examples:
            >>> account = SavingsAccount("ACC001", "CUST001", Money(1000, Currency.USD), 0.05)
            >>> interest = account.calculate_interest()
            >>> print(interest.amount)
            50.0
        """
        interest_amount = self._balance.amount * self._interest_rate
        return Money(interest_amount, self._balance.currency)
    
    def apply_interest(self) -> Money:
        """
        Calculate and apply interest to the account balance.
        
        This method:
        1. Calculates interest based on current balance
        2. Adds interest to balance
        3. Creates an INTEREST transaction
        4. Returns the interest amount earned
        
        Returns:
            Money: Interest amount that was added
        
        Examples:
            >>> account = SavingsAccount("ACC001", "CUST001", Money(1000, Currency.USD), 0.05)
            >>> interest = account.apply_interest()
            >>> print(f"Interest earned: {interest}")
            Interest earned: 50.00 USD
            >>> print(f"New balance: {account.balance}")
            New balance: 1050.00 USD
        """
        # Calculate interest
        interest = self.calculate_interest()
        
        # Only apply if interest is positive
        if interest.amount <= 0:
            return Money.zero(self._balance.currency)
        
        # Update balance
        self._balance = self._balance + interest
        
        # Create INTEREST transaction
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            transaction_type=TransactionType.INTEREST,
            amount=interest,
            description=f"Interest at {self._interest_rate * 100:.2f}% annual rate",
            account_number=self._account_number
        )
        
        # Log transaction
        self._transactions.append(transaction)
        
        return interest
    
    def __str__(self) -> str:
        """String representation."""
        return (f"SavingsAccount({self._account_number}): {self._balance}, "
                f"Interest Rate: {self._interest_rate * 100:.2f}%")
    
    def __repr__(self) -> str:
        """Developer representation."""
        return (f"SavingsAccount(account_number={self._account_number}, "
                f"balance={self._balance}, interest_rate={self._interest_rate})")