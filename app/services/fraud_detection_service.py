"""
Fraud Detection Service

Security service to detect suspicious transactions.
"""

from typing import Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.account import Account
from models.value_objects import Money


class FraudDetectionService:
    """
    Fraud detection service with rule-based checks.
    
    Implements security rules to prevent fraudulent transactions.
    
    Rules:
    1. Transactions over 10,000 are flagged as high-risk
    2. Negative amounts are rejected
    3. Additional rules can be added easily
    
    Examples:
        >>> service = FraudDetectionService()
        >>> is_valid, message = service.check_transaction(account, Money(5000, Currency.USD))
        >>> if not is_valid:
        ...     print(f"Fraud detected: {message}")
    """
    
    # Fraud detection thresholds
    HIGH_AMOUNT_THRESHOLD = 10000.0
    
    def __init__(self):
        """Initialize fraud detection service."""
        self._fraud_attempts = 0
    
    def check_transaction(self, account: Account, amount: Money) -> Tuple[bool, str]:
        """
        Check if a transaction is suspicious.
        
        Applies multiple fraud detection rules:
        - Rule 1: Amount must not exceed 10,000
        - Rule 2: Amount must be positive
        
        Args:
            account: Account attempting the transaction
            amount: Transaction amount to validate
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
                - is_valid: True if transaction passes all checks
                - message: Explanation of result
        
        Examples:
            >>> service = FraudDetectionService()
            >>> account = Account("ACC001", "CUST001", Money(5000, Currency.USD))
            >>> 
            >>> # Valid transaction
            >>> is_valid, msg = service.check_transaction(account, Money(100, Currency.USD))
            >>> print(is_valid)
            True
            >>> 
            >>> # High amount fraud
            >>> is_valid, msg = service.check_transaction(account, Money(15000, Currency.USD))
            >>> print(is_valid)
            False
            >>> print(msg)
            Fraud Risk: Amount exceeds limit of 10,000.00
        """
        # Rule 2: Amount must not be negative
        if amount.amount < 0:
            self._fraud_attempts += 1
            return False, "Fraud Risk: Negative amounts are not allowed"
        
        # Rule 1: Amount must not exceed threshold
        if amount.amount > self.HIGH_AMOUNT_THRESHOLD:
            self._fraud_attempts += 1
            return False, f"Fraud Risk: Amount exceeds limit of {self.HIGH_AMOUNT_THRESHOLD:,.2f}"
        
        # All checks passed
        return True, "Transaction approved"
    
    def check_withdrawal(self, account: Account, amount: Money) -> Tuple[bool, str]:
        """
        Check if a withdrawal is suspicious.
        
        Additional checks specific to withdrawals.
        
        Args:
            account: Account attempting withdrawal
            amount: Withdrawal amount
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        # First run standard transaction checks
        is_valid, message = self.check_transaction(account, amount)
        
        if not is_valid:
            return is_valid, message
        
        # Additional withdrawal-specific checks can be added here
        # For example: check withdrawal frequency, unusual patterns, etc.
        
        return True, "Withdrawal approved"
    
    def check_deposit(self, account: Account, amount: Money) -> Tuple[bool, str]:
        """
        Check if a deposit is suspicious.
        
        Additional checks specific to deposits.
        
        Args:
            account: Account receiving deposit
            amount: Deposit amount
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        # First run standard transaction checks
        is_valid, message = self.check_transaction(account, amount)
        
        if not is_valid:
            return is_valid, message
        
        # Additional deposit-specific checks can be added here
        # For example: check for money laundering patterns
        
        return True, "Deposit approved"
    
    def get_fraud_attempts(self) -> int:
        """
        Get total number of fraud attempts detected.
        
        Returns:
            int: Number of fraudulent transactions blocked
        """
        return self._fraud_attempts
    
    def reset_fraud_counter(self) -> None:
        """Reset the fraud attempt counter."""
        self._fraud_attempts = 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"FraudDetectionService(fraud_attempts={self._fraud_attempts})"