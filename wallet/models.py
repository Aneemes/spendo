from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.db import models

from core.models_mixin import IdentifierTimeStampAbstractModel

class Wallet(IdentifierTimeStampAbstractModel):
    title = models.CharField(max_length=125)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='wallet')
    color = models.CharField(max_length=7, default="#007bff")

    def __str__(self):
        return self.title
    
    @transaction.atomic
    def deposit(self, amount: Decimal):
        """Add amount to wallet balance"""
        self.balance += amount
        self.save()
        
    @transaction.atomic
    def withdraw(self, amount: Decimal):
        """Subtract amount from wallet balance"""
        self.balance -= amount
        self.save()
    
    @transaction.atomic
    def transfer_balance(self, to_wallet, amount: Decimal):
        """Transfer amount from this wallet to another wallet"""
        self.withdraw(amount)
        to_wallet.deposit(amount)
    
    class Meta:
        db_table="user_wallet"
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"
        unique_together = ('title', 'user')

class TransferTransaction(IdentifierTimeStampAbstractModel):
    """
    Model representing a transfer transaction between wallets.
    
    Attributes:
        source_wallet (ForeignKey): The wallet from which funds are transferred.
        destination_wallet (ForeignKey): The wallet to which funds are transferred.
        amount (DecimalField): The amount transferred.
        description (TextField): Optional description for the transfer.
        user (ForeignKey): The user who performed the transfer.
        date (DateField): The date when the transfer was made.
    """
    source_wallet = models.ForeignKey("wallet.Wallet", on_delete=models.SET_NULL, null=True, related_name='transfers_sent')
    destination_wallet = models.ForeignKey("wallet.Wallet", on_delete=models.SET_NULL, null=True, related_name='transfers_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='transfers')
    date = models.DateField(default=timezone.now)

    class Meta:
        db_table = "wallet_transfers"
        verbose_name = "Wallet Transfer"
        verbose_name_plural = "Wallet Transfers"