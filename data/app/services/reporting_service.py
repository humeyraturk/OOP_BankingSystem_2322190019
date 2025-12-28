"""
Reporting Service

ALGORITHM 4: Report generator with monthly summaries.
"""

from typing import List, Dict, Any
from collections import defaultdict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.transaction import Transaction, TransactionType


class ReportingService:
    """
    Report generator for financial summaries.
    
    Generates monthly reports grouping transactions and calculating
    income vs expenses.
    """
    
    @staticmethod
    def generate_monthly_summary(transactions: List[Transaction]) -> Dict[str, Dict[str, Any]]:
        """
        Generate monthly summary report grouped by YYYY-MM.
        
        For each month, calculates:
        - Total income (deposits)
        - Total expenses (withdrawals)
        - Net change (income - expenses)
        - Transaction count
        
        Args:
            transactions: All transactions to analyze
        
        Returns:
            Dict[str, Dict[str, Any]]: Monthly summaries keyed by "YYYY-MM"
        
        Examples:
            >>> service = ReportingService()
            >>> summary = service.generate_monthly_summary(all_transactions)
            >>> 
            >>> # Access specific month
            >>> jan_2024 = summary['2024-01']
            >>> print(f"Income: ${jan_2024['total_income']:.2f}")
            >>> print(f"Expenses: ${jan_2024['total_expenses']:.2f}")
            >>> print(f"Net: ${jan_2024['net_change']:.2f}")
        """
        if not transactions:
            return {}
        
        # Dictionary to store monthly data
        monthly_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_income': 0.0,
            'total_expenses': 0.0,
            'net_change': 0.0,
            'transaction_count': 0,
            'by_type': defaultdict(int)
        })
        
        # Process each transaction
        for txn in transactions:
            # Get month key (YYYY-MM format)
            month_key = txn.timestamp.strftime("%Y-%m")
            
            # Get month data
            month = monthly_data[month_key]
            
            # Update transaction count
            month['transaction_count'] += 1
            
            # Update type breakdown
            month['by_type'][txn.transaction_type.value] += 1
            
            # Calculate income and expenses
            amount = txn.amount.amount
            
            if txn.transaction_type in [TransactionType.DEPOSIT, TransactionType.INTEREST]:
                month['total_income'] += amount
            elif txn.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.FEE]:
                month['total_expenses'] += amount
        
        # Calculate net change for each month
        for month_key in monthly_data:
            month = monthly_data[month_key]
            month['net_change'] = month['total_income'] - month['total_expenses']
            
            # Round to 2 decimal places
            month['total_income'] = round(month['total_income'], 2)
            month['total_expenses'] = round(month['total_expenses'], 2)
            month['net_change'] = round(month['net_change'], 2)
            
            # Convert defaultdict to regular dict
            month['by_type'] = dict(month['by_type'])
        
        return dict(monthly_data)
    
    @staticmethod
    def generate_text_report(transactions: List[Transaction], title: str = "Financial Report") -> str:
        """
        Generate human-readable text report.
        
        Args:
            transactions: Transactions to report on
            title: Report title
        
        Returns:
            str: Formatted text report
        """
        if not transactions:
            return f"{title}\n{'='*50}\nNo transactions to report."
        
        monthly = ReportingService.generate_monthly_summary(transactions)
        
        lines = []
        lines.append("=" * 70)
        lines.append(f"{title:^70}")
        lines.append("=" * 70)
        lines.append("")
        
        # Overall summary
        total_income = sum(m['total_income'] for m in monthly.values())
        total_expenses = sum(m['total_expenses'] for m in monthly.values())
        net_change = total_income - total_expenses
        
        lines.append("OVERALL SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Income:    ${total_income:>12,.2f}")
        lines.append(f"Total Expenses:  ${total_expenses:>12,.2f}")
        lines.append(f"Net Change:      ${net_change:>12,.2f}")
        lines.append("")
        
        # Monthly breakdown
        lines.append("MONTHLY BREAKDOWN")
        lines.append("-" * 70)
        lines.append(f"{'Month':<12} {'Income':>15} {'Expenses':>15} {'Net':>15}")
        lines.append("-" * 70)
        
        for month_key in sorted(monthly.keys()):
            month_data = monthly[month_key]
            lines.append(
                f"{month_key:<12} "
                f"${month_data['total_income']:>14,.2f} "
                f"${month_data['total_expenses']:>14,.2f} "
                f"${month_data['net_change']:>14,.2f}"
            )
        
        lines.append("=" * 70)
        
        return "\n".join(lines)