"""
Transaction Service

ALGORITHM 3: Transaction search and filtering algorithm.
"""

from typing import List, Dict, Any
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.transaction import Transaction, TransactionType


class TransactionService:
    """
    Transaction search and filtering service.
    
    Provides efficient filtering algorithms for transactions.
    """
    
    @staticmethod
    def search_transactions(
        transactions: List[Transaction],
        criteria: Dict[str, Any]
    ) -> List[Transaction]:
        """
        Search and filter transactions based on criteria.
        
        Supported Criteria:
        - start_date (datetime): Filter transactions after this date
        - end_date (datetime): Filter transactions before this date
        - transaction_type (TransactionType): Filter by type
        - min_amount (float): Filter by minimum amount
        - max_amount (float): Filter by maximum amount
        
        Args:
            transactions: List of transactions to search
            criteria: Dictionary of search criteria
        
        Returns:
            List[Transaction]: Filtered transactions
        
        Examples:
            >>> # Filter by date range
            >>> criteria = {
            ...     'start_date': datetime(2024, 1, 1),
            ...     'end_date': datetime(2024, 12, 31)
            ... }
            >>> results = TransactionService.search_transactions(txns, criteria)
            
            >>> # Filter by type and amount
            >>> criteria = {
            ...     'transaction_type': TransactionType.DEPOSIT,
            ...     'min_amount': 1000.0
            ... }
            >>> results = TransactionService.search_transactions(txns, criteria)
        """
        if not transactions:
            return []
        
        if not criteria:
            return transactions.copy()
        
        # Extract criteria
        start_date = criteria.get('start_date')
        end_date = criteria.get('end_date')
        transaction_type = criteria.get('transaction_type')
        min_amount = criteria.get('min_amount')
        max_amount = criteria.get('max_amount')
        
        # Filter transactions
        results = []
        
        for txn in transactions:
            # Check start_date
            if start_date is not None and txn.timestamp < start_date:
                continue
            
            # Check end_date
            if end_date is not None and txn.timestamp > end_date:
                continue
            
            # Check transaction_type
            if transaction_type is not None and txn.transaction_type != transaction_type:
                continue
            
            # Check min_amount
            if min_amount is not None and txn.amount.amount < min_amount:
                continue
            
            # Check max_amount
            if max_amount is not None and txn.amount.amount > max_amount:
                continue
            
            # All criteria passed
            results.append(txn)
        
        return results
    
    @staticmethod
    def filter_by_type(
        transactions: List[Transaction],
        transaction_type: TransactionType
    ) -> List[Transaction]:
        """Filter transactions by type."""
        return TransactionService.search_transactions(
            transactions,
            {'transaction_type': transaction_type}
        )