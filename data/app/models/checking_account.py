"""
Checking Account Module

Checking account with overdraft protection.
"""

from datetime import datetime
import uuid
from .account import Account
from .value_objects import Money
from .transaction import Transaction, TransactionType


class CheckingAccount(Account):
    """
    Checking account with overdraft protection.
    
    This account type allows the balance to go negative up to a
    specified overdraft limit, providing financial flexibility.
    
    Attributes:
        overdraft_limit: Maximum negative balance allowed
    
    Examples:
        >>> account = CheckingAccount(
        ...     "ACC001",
        ...     "CUST001",
        ...     Money(500.0, Currency.USD),
        ...     overdraft_limit=1000.0
        ... )
        >>> # Can withdraw more than balance
        >>> account.withdraw(Money(1200.0, Currency.USD))
        True
        >>> print(account.balance)
        -700.00 USD
    """
    
    def __init__(
        self,
        account_number: str,
        owner_id: str,
        initial_balance: Money,
        overdraft_limit: float = 1000.0
    ):
        """
        Initialize a checking account.
        
        Args:
            account_number: Unique account identifier
            owner_id: Customer ID
            initial_balance: Starting balance
            overdraft_limit: Maximum overdraft allowed (default: 1000.0)
        
        Raises:
            ValueError: If overdraft limit is negative
        """
        super().__init__(account_number, owner_id, initial_balance)
        
        if overdraft_limit < 0:
            raise ValueError("Overdraft limit cannot be negative")
        
        self._overdraft_limit: float = overdraft_limit
    
    @property
    def overdraft_limit(self) -> float:
        """Get the overdraft limit."""
        return self._overdraft_limit
    
    @overdraft_limit.setter
    def overdraft_limit(self, value: float) -> None:
        """
        Set the overdraft limit.
        
        Args:
            value: New overdraft limit
        
        Raises:
            ValueError: If limit is negative
        """
        if value < 0:
            raise ValueError("Overdraft limit cannot be negative")
        self._overdraft_limit = value
    
    def get_available_balance(self) -> Money:
        """
        Get total available balance including overdraft.
        
        Returns:
            Money: Current balance + overdraft limit
        
        Examples:
            >>> account = CheckingAccount("ACC001", "CUST001", Money(500, Currency.USD), 1000)
            >>> available = account.get_available_balance()
            >>> print(available.amount)
            1500.0
        """
        available = self._balance.amount + self._overdraft_limit
        return Money(available, self._balance.currency)
    
    def is_overdrawn(self) -> bool:
        """
        Check if account is currently overdrawn (negative balance).
        
        Returns:
            bool: True if balance is negative
        
        Examples:
            >>> account = CheckingAccount("ACC001", "CUST001", Money(-200, Currency.USD), 1000)
            >>> account.is_overdrawn()
            True
        """
        return self._balance.amount < 0
    
    def withdraw(self, amount: Money, description: str = "") -> bool:
        """
        Withdraw money from checking account with overdraft protection.
        
        Allows withdrawal if: (balance + overdraft_limit) >= amount
        
        Args:
            amount: Amount to withdraw (must be positive)
            description: Transaction description
        
        Returns:
            bool: True if withdrawal successful, False if exceeds limit
        
        Raises:
            ValueError: If amount is invalid
        
        Examples:
            >>> account = CheckingAccount("ACC001", "CUST001", Money(500, Currency.USD), 1000)
            >>> # Withdraw more than balance but within overdraft
            >>> account.withdraw(Money(1200, Currency.USD))
            True
            >>> print(account.balance)
            -700.00 USD
            
            >>> # Withdraw exceeding overdraft limit
            >>> account.withdraw(Money(500, Currency.USD))
            False  # Would exceed overdraft limit
        """
        # Validation: amount must be positive
        if not isinstance(amount, Money):
            raise TypeError(f"Amount must be Money object, got {type(amount).__name__}")
        
        if amount.amount <= 0:
            raise ValueError(f"Amount must be positive, got {amount.amount}")
        
        # Validation: currency must match
        if amount.currency != self._balance.currency:
            raise ValueError(
                f"Currency mismatch: account uses {self._balance.currency.value}, "
                f"but {amount.currency.value} was provided"
            )
        
        # Check if withdrawal is within overdraft limit
        # Available = balance + overdraft_limit
        available = self._balance.amount + self._overdraft_limit
        
        if amount.amount > available:
            return False  # Exceeds overdraft limit
        
        # Update balance (can go negative)
        self._balance = self._balance - amount
        
        # Create transaction
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            description=description or "Withdrawal",
            account_number=self._account_number
        )
        
        # Log transaction
        self._transactions.append(transaction)
        
        return True
    
    def __str__(self) -> str:
        """String representation."""
        overdraft_info = ""
        if self.is_overdrawn():
            overdraft_info = f" (OVERDRAWN)"
        
        return (f"CheckingAccount({self._account_number}): {self._balance}{overdraft_info}, "
                f"Overdraft Limit: {self._overdraft_limit:.2f}")
    
    def __repr__(self) -> str:
        """Developer representation."""
        return (f"CheckingAccount(account_number={self._account_number}, "
                f"balance={self._balance}, overdraft_limit={self._overdraft_limit})")