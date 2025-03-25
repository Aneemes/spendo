from typing import Dict, List
from collections import defaultdict

from rest_framework.exceptions import ValidationError as DRFValidationError

from income.models import Income
from expense.models import Expense
from account.models import CustomUser
from wallet.models import TransferTransaction

from .dataclasses import (
    ExpenseTransactionData,
    IncomeTransactionData,
    TransferTransactionData,
    DateGroup
)


def get_transaction_list(
    year: str,
    month: str,
    user: CustomUser,
    transaction_type: str = 'all',
) -> List[Dict]:
    """
    Get transaction list for a user for a specific month and year,
    grouped by date with daily totals.
    
    Args:
        year (str): Year to filter transactions
        month (str): Month to filter transactions
        user (CustomUser): User whose transactions to retrieve
        transaction_type (str, optional): Type of transactions to retrieve.
            Valid values are 'all', 'expense', 'income', 'transfer'. Defaults to 'all'.
            
    Returns:
        list: List of dictionaries containing date, amount, and transactions
        
    Raises:
        DRFValidationError: If an invalid transaction type is provided
    """
    # Validate transaction_type
    valid_types = {'all', 'expense', 'income', 'transfer'}
    if transaction_type not in valid_types:
        raise DRFValidationError(detail=f"Invalid transaction type. Valid options are {', '.join(valid_types)}.")
    
    # Dictionary to hold transactions grouped by date
    date_groups = defaultdict(lambda: DateGroup(date=None))
    
    # Create base filters
    expense_filters = {'user': user, 'date__year': year}
    income_filters = {'user': user, 'date__year': year}
    transfer_filters = {'user': user, 'date__year': year}
    
    # Add month filter if specified
    if month:
        expense_filters['date__month'] = month
        income_filters['date__month'] = month
        transfer_filters['date__month'] = month
    
    # Fetch and process expense transactions if needed
    if transaction_type in ('all', 'expense'):
        expenses = (Expense.objects.filter(**expense_filters)
                   .select_related('category', 'wallet')
                   .order_by('date'))
        
        for expense in expenses:
            transaction = ExpenseTransactionData.from_expense(expense)
            date_group = date_groups[expense.date]
            date_group.date = expense.date
            date_group.amount -= expense.amount
            date_group.transactions.append(transaction)
    
    # Fetch and process income transactions if needed
    if transaction_type in ('all', 'income'):
        incomes = (Income.objects.filter(**income_filters)
         .select_related('category', 'wallet')
         .order_by('date'))
        
        for income in incomes:
            transaction = IncomeTransactionData.from_income(income)
            date_group = date_groups[income.date]
            date_group.date = income.date
            date_group.amount += income.amount
            date_group.transactions.append(transaction)
    
    # Fetch and process transfer transactions if needed
    if transaction_type in ('all', 'transfer'):
        transfers = (TransferTransaction.objects.filter(**transfer_filters)
         .select_related('source_wallet', 'destination_wallet')
         .order_by('date'))
        
        for transfer in transfers:
            transaction = TransferTransactionData.from_transfer(transfer)
            date_group = date_groups[transfer.date]
            date_group.date = transfer.date
            # Transfers don't affect the daily total
            date_group.transactions.append(transaction)
    
    # Convert dataclasses to dictionaries for serialization
    result = []
    for date in sorted(date_groups.keys()):
        group = date_groups[date]
        
        # Convert transactions to serializable dictionaries
        transaction_dicts = []
        for transaction in group.transactions:
            # Convert dataclass to dict, handling nested dataclasses
            transaction_dict = transaction.__dict__.copy()
            
            # Handle nested dataclasses for expense/income transactions
            if isinstance(transaction, (ExpenseTransactionData, IncomeTransactionData)):
                if transaction.category:
                    transaction_dict['category'] = transaction.category.__dict__
                if transaction.wallet:
                    transaction_dict['wallet'] = transaction.wallet.__dict__
                    
            # Handle nested dataclasses for transfer transactions
            elif isinstance(transaction, TransferTransactionData):
                if transaction.source_wallet:
                    transaction_dict['source_wallet'] = transaction.source_wallet.__dict__
                if transaction.destination_wallet:
                    transaction_dict['destination_wallet'] = transaction.destination_wallet.__dict__
            
            transaction_dicts.append(transaction_dict)
        
        result.append({
            'date': group.date,
            'amount': group.amount,
            'transactions': transaction_dicts
        })
    
    return result
