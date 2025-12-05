"""
Transaction Module

Represents financial transactions in the banking system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from .value_objects import Money


class TransactionType(Enum):
    """
    Enumeration of transaction types.
    
    Attributes:
        DEPOSIT: Money added to account
        WITHDRAWAL: Money removed from account
        TRANSFER: Money moved between accounts
        INTEREST: Interest credited
        FEE: Fee charged
    """
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    INTEREST = "INTEREST"
    FEE = "FEE"


@dataclass
class Transaction:
    """
    Represents a financial transaction.
    
    Attributes:
        transaction_id: Unique identifier
        timestamp: When the transaction occurred
        transaction_type: Type of transaction
        amount: Transaction amount as Money object
        description: Human-readable description
        account_number: Associated account
        related_account: For transfers, the other account
    """
    transaction_id: str
    timestamp: datetime
    transaction_type: TransactionType
    amount: Money
    description: str
    account_number: str
    related_account: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of transaction."""
        return f"{self.transaction_type.value}: {self.amount} - {self.description}"