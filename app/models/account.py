"""
Account Module

Abstract base class and account hierarchy for the banking system.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .value_objects import Money
from .transaction import Transaction


class AbstractAccount(ABC):
    """
    Abstract base class for all account types.
    
    This class defines the contract that all concrete account
    implementations must follow, ensuring polymorphic behavior.
    
    Attributes:
        account_number: Unique account identifier
        owner_id: Customer ID who owns this account
        balance: Current account balance
        transactions: List of all transactions
    """
    
    def __init__(
        self,
        account_number: str,
        owner_id: str,
        initial_balance: Money
    ) -> None:
        """
        Initialize an account.
        
        Args:
            account_number: Unique account identifier
            owner_id: Customer ID
            initial_balance: Starting balance
        """
        self._account_number: str = account_number
        self._owner_id: str = owner_id
        self._balance: Money = initial_balance
        self._transactions: List[Transaction] = []
    
    @property
    def account_number(self) -> str:
        """Get account number."""
        return self._account_number
    
    @property
    def owner_id(self) -> str:
        """Get owner's customer ID."""
        return self._owner_id
    
    @property
    def balance(self) -> Money:
        """Get current balance."""
        return self._balance
    
    @property
    def transactions(self) -> List[Transaction]:
        """Get transaction history."""
        return self._transactions.copy()
    
    @abstractmethod
    def deposit(self, amount: Money, description: str = "") -> bool:
        """
        Deposit money into account.
        
        Args:
            amount: Amount to deposit
            description: Transaction description
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def withdraw(self, amount: Money, description: str = "") -> bool:
        """
        Withdraw money from account.
        
        Args:
            amount: Amount to withdraw
            description: Transaction description
        
        Returns:
            True if successful, False if insufficient funds
        """
        pass
    
    def get_balance(self) -> Money:
        """
        Get current balance.
        
        Returns:
            Current account balance
        """
        return self._balance
    
    def get_transaction_history(self) -> List[Transaction]:
        """
        Get complete transaction history.
        
        Returns:
            List of all transactions
        """
        return self._transactions.copy()
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({self._account_number}): {self._balance}"