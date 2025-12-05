"""
Customer Module

Represents bank customers and their relationships with accounts.
"""

from typing import List, Optional
from .account import AbstractAccount


class Customer:
    """
    Represents a bank customer.
    
    A customer can own multiple accounts and provides
    aggregate operations across all their accounts.
    
    Attributes:
        customer_id: Unique customer identifier
        name: Customer's full name
        email: Customer's email address
        phone: Customer's phone number
        accounts: List of customer's accounts
    """
    
    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str
    ) -> None:
        """
        Initialize a customer.
        
        Args:
            customer_id: Unique identifier
            name: Full name
            email: Email address
            phone: Phone number
        """
        self._customer_id: str = customer_id
        self._name: str = name
        self._email: str = email
        self._phone: str = phone
        self._accounts: List[AbstractAccount] = []
    
    @property
    def customer_id(self) -> str:
        """Get customer ID."""
        return self._customer_id
    
    @property
    def name(self) -> str:
        """Get customer name."""
        return self._name
    
    @property
    def email(self) -> str:
        """Get customer email."""
        return self._email
    
    @property
    def phone(self) -> str:
        """Get customer phone."""
        return self._phone
    
    @property
    def accounts(self) -> List[AbstractAccount]:
        """Get list of customer accounts."""
        return self._accounts.copy()
    
    def add_account(self, account: AbstractAccount) -> None:
        """
        Add an account to this customer.
        
        Args:
            account: Account to add
        """
        self._accounts.append(account)
    
    def get_account(self, account_number: str) -> Optional[AbstractAccount]:
        """
        Get a specific account by number.
        
        Args:
            account_number: Account number to find
        
        Returns:
            Account if found, None otherwise
        """
        for account in self._accounts:
            if account.account_number == account_number:
                return account
        return None
    
    def __str__(self) -> str:
        """String representation."""
        return f"Customer({self._customer_id}, {self._name}, {len(self._accounts)} accounts)"