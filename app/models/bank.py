"""
Bank Module

Central aggregate root for the banking system.
Manages customers, accounts, and coordinates operations.
"""

from typing import Dict, List, Optional
from .customer import Customer
from .account import AbstractAccount


class Bank:
    """
    Central bank aggregate root.
    
    The Bank class acts as the main repository and facade,
    coordinating all operations between customers and accounts.
    
    Attributes:
        name: Bank name
        customers: Dictionary of customers by ID
        accounts: Dictionary of accounts by account number
    """
    
    def __init__(self, name: str = "International Bank") -> None:
        """
        Initialize the bank.
        
        Args:
            name: Name of the bank
        """
        self._name: str = name
        self._customers: Dict[str, Customer] = {}
        self._accounts: Dict[str, AbstractAccount] = {}
    
    @property
    def name(self) -> str:
        """Get bank name."""
        return self._name
    
    def create_customer(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str
    ) -> Customer:
        """
        Create a new customer.
        
        Args:
            customer_id: Unique customer ID
            name: Customer name
            email: Customer email
            phone: Customer phone
        
        Returns:
            Newly created Customer object
        """
        customer = Customer(customer_id, name, email, phone)
        self._customers[customer_id] = customer
        return customer
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """
        Retrieve a customer by ID.
        
        Args:
            customer_id: Customer ID to look up
        
        Returns:
            Customer if found, None otherwise
        """
        return self._customers.get(customer_id)
    
    def register_account(self, account: AbstractAccount) -> None:
        """
        Register an account with the bank.
        
        Args:
            account: Account to register
        """
        self._accounts[account.account_number] = account
    
    def get_account(self, account_number: str) -> Optional[AbstractAccount]:
        """
        Retrieve an account by number.
        
        Args:
            account_number: Account number to look up
        
        Returns:
            Account if found, None otherwise
        """
        return self._accounts.get(account_number)
    
    def get_all_customers(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List of all customers
        """
        return list(self._customers.values())
    
    def get_all_accounts(self) -> List[AbstractAccount]:
        """
        Get all accounts.
        
        Returns:
            List of all accounts
        """
        return list(self._accounts.values())
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self._name}: {len(self._customers)} customers, {len(self._accounts)} accounts"