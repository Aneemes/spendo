from dataclasses import dataclass, field
from datetime import date as date_type
from decimal import Decimal
from typing import List, Optional, Any
from uuid import UUID

from expense.models import Expense
from income.models import Income
from wallet.models import TransferTransaction


@dataclass
class CategoryData:
    uid: UUID
    title: str
    color_code: str


@dataclass
class WalletData:
    uid: UUID
    title: str


@dataclass
class BaseTransaction:
    uid: UUID
    date: date_type
    title: str
    amount: Decimal
    description: Optional[str]
    transaction_type: str


@dataclass
class ExpenseTransactionData(BaseTransaction):
    category: Optional[CategoryData] = None
    wallet: Optional[WalletData] = None
    
    @classmethod
    def from_expense(cls, expense: Expense) -> 'ExpenseTransactionData':
        category_data = None
        if expense.category:
            category_data = CategoryData(
                uid=expense.category.uid,
                title=expense.category.title,
                color_code=expense.category.color_code
            )
        
        wallet_data = None
        if expense.wallet:
            wallet_data = WalletData(
                uid=expense.wallet.uid,
                title=expense.wallet.title
            )
        
        return cls(
            uid=expense.uid,
            date=expense.date,
            title=expense.title or "Expense",
            amount=expense.amount,
            description=expense.description,
            transaction_type='expense',
            category=category_data,
            wallet=wallet_data
        )


@dataclass
class IncomeTransactionData(BaseTransaction):
    category: Optional[CategoryData] = None
    wallet: Optional[WalletData] = None
    
    @classmethod
    def from_income(cls, income: Income) -> 'IncomeTransactionData':
        category_data = None
        if income.category:
            category_data = CategoryData(
                uid=income.category.uid,
                title=income.category.title,
                color_code=income.category.color_code
            )
        
        wallet_data = None
        if income.wallet:
            wallet_data = WalletData(
                uid=income.wallet.uid,
                title=income.wallet.title
            )
        
        return cls(
            uid=income.uid,
            date=income.date,
            title=income.title or "Income",
            amount=income.amount,
            description=income.description,
            transaction_type='income',
            category=category_data,
            wallet=wallet_data
        )


@dataclass
class TransferTransactionData(BaseTransaction):
    source_wallet: Optional[WalletData] = None
    destination_wallet: Optional[WalletData] = None
    
    @classmethod
    def from_transfer(cls, transfer: TransferTransaction) -> 'TransferTransactionData':
        source_wallet_data = None
        if transfer.source_wallet:
            source_wallet_data = WalletData(
                uid=transfer.source_wallet.uid,
                title=transfer.source_wallet.title
            )
        
        destination_wallet_data = None
        if transfer.destination_wallet:
            destination_wallet_data = WalletData(
                uid=transfer.destination_wallet.uid,
                title=transfer.destination_wallet.title
            )
        
        title = "Transfer"
        if transfer.source_wallet and transfer.destination_wallet:
            title = f"Transfer: {transfer.source_wallet.title} → {transfer.destination_wallet.title}"
        
        return cls(
            uid=transfer.uid,
            date=transfer.date,
            title=title,
            amount=transfer.amount,
            description=transfer.description,
            transaction_type='transfer',
            source_wallet=source_wallet_data,
            destination_wallet=destination_wallet_data
        )


@dataclass
class DateGroup:
    date: date_type
    amount: Decimal = Decimal('0')
    transactions: List[Any] = field(default_factory=list)

