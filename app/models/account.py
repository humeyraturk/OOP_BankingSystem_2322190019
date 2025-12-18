"""
Account Module

Abstract base class and concrete account implementation with business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Generator, Tuple
from datetime import datetime
import uuid
from .value_objects import Money, Currency
from .transaction import Transaction, TransactionType


class AbstractAccount(ABC):
    """
    Abstract base class for all account types.
    
    Attributes:
        account_number: Unique account identifier
        owner_id: Customer ID
        balance: Current balance
        transactions: Transaction history
    """
    
    def __init__(self, account_number: str, owner_id: str, initial_balance: Money):
        """Initialize account."""
        if initial_balance.amount < 0:
            raise ValueError("Initial balance cannot be negative")
        
        self._account_number: str = account_number
        self._owner_id: str = owner_id
        self._balance: Money = initial_balance
        self._transactions: List[Transaction] = []
        
        # Record initial deposit
        if initial_balance.amount > 0:
            initial_txn = Transaction(
                transaction_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                transaction_type=TransactionType.DEPOSIT,
                amount=initial_balance,
                description="Initial deposit",
                account_number=self._account_number
            )
            self._transactions.append(initial_txn)
    
    @property
    def account_number(self) -> str:
        return self._account_number
    
    @property
    def owner_id(self) -> str:
        return self._owner_id
    
    @property
    def balance(self) -> Money:
        return self._balance
    
    @property
    def transactions(self) -> List[Transaction]:
        return self._transactions.copy()
    
    @abstractmethod
    def deposit(self, amount: Money, description: str = "") -> bool:
        """Deposit money into account."""
        pass
    
    @abstractmethod
    def withdraw(self, amount: Money, description: str = "") -> bool:
        """Withdraw money from account."""
        pass
    
    def get_balance(self) -> Money:
        """Get current balance."""
        return self._balance
    
    def get_transaction_history(self) -> List[Transaction]:
        """Get complete transaction history."""
        return self._transactions.copy()
    
    def get_running_balance(self) -> Generator[Tuple[Transaction, Money], None, None]:
        """
        ALGORITHM 1: Running Balance Generator
        
        Yields each transaction with the balance after that transaction.
        Uses Python generator for memory efficiency.
        
        Yields:
            Tuple[Transaction, Money]: Transaction and balance after it
        
        Examples:
            >>> for txn, balance in account.get_running_balance():
            ...     print(f"{txn.timestamp}: {balance}")
        """
        current_balance = Money.zero(self._balance.currency)
        
        for transaction in self._transactions:
            # Update balance based on transaction type
            if transaction.transaction_type in [TransactionType.DEPOSIT, TransactionType.INTEREST]:
                current_balance = current_balance + transaction.amount
            elif transaction.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.FEE]:
                current_balance = current_balance - transaction.amount
            
            yield (transaction, current_balance)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._account_number}): {self._balance}"


class Account(AbstractAccount):
    """
    Concrete account implementation with deposit and withdraw logic.
    
    Examples:
        >>> account = Account("ACC001", "CUST001", Money(1000.0, Currency.USD))
        >>> account.deposit(Money(500.0, Currency.USD), "Salary")
        True
        >>> account.withdraw(Money(200.0, Currency.USD), "ATM")
        True
    """
    
    def deposit(self, amount: Money, description: str = "") -> bool:
        """
        Deposit money into account.
        
        Args:
            amount: Amount to deposit (must be positive)
            description: Transaction description
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If amount is invalid
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
        
        # Update balance
        self._balance = self._balance + amount
        
        # Create transaction
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            description=description or "Deposit",
            account_number=self._account_number
        )
        
        # Append to transactions
        self._transactions.append(transaction)
        
        return True
    
    def withdraw(self, amount: Money, description: str = "") -> bool:
        """
        Withdraw money from account.
        
        Args:
            amount: Amount to withdraw (must be positive)
            description: Transaction description
        
        Returns:
            True if successful, False if insufficient funds
        
        Raises:
            ValueError: If amount is invalid
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
        
        # Check sufficient funds
        if amount > self._balance:
            return False  # Insufficient funds
        
        # Update balance
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