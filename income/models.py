from django.utils import timezone
from django.db import models, transaction

from core.models_mixin import IdentifierTimeStampAbstractModel
from core.models import IncomeCategory

class Income(IdentifierTimeStampAbstractModel):
    """
    A model representing an income record in the system.
    This model tracks financial income entries with details such as title, amount,
    date, description, category, and associated user.
    Attributes:
        title (CharField): The title of the income entry (optional, max length: 255)
        amount (DecimalField): The monetary amount of the income (max digits: 10, decimal places: 2)
        date (DateField): The date when the income was received
        description (TextField): Additional details about the income (optional)
        category (ForeignKey): Reference to IncomeCategory model (optional)
        user (ForeignKey): Reference to CustomUser model who owns this income record
    Inherits:
        IdentifierTimeStampAbstractModel: Provides basic identifier and timestamp fields
    Meta:
        db_table: 'income'
        verbose_name: 'Income'
        verbose_name_plural: 'Incomes'
    """
    title = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("core.IncomeCategory", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='income')
    wallet = models.ForeignKey("wallet.Wallet", on_delete=models.SET_NULL, null=True, related_name='income')

    def clean(self):
        with transaction.atomic():
            if self.pk:
                # Existing instance, handle updates
                previous = Income.objects.get(pk=self.pk)
                
                # Handle wallet change
                if previous.wallet and previous.wallet != self.wallet:
                    # Revert amount from previous wallet
                    previous.wallet.withdraw(previous.amount)
                    
                    # Add to new wallet if it exists
                    if self.wallet:
                        self.wallet.deposit(self.amount)
                
                # Handle amount change for same wallet
                elif previous.wallet == self.wallet and self.wallet and previous.amount != self.amount:
                    # Adjust the difference
                    difference = self.amount - previous.amount
                    self.wallet.deposit(difference)
            else:
                # New instance, add to wallet
                if self.wallet:
                    self.wallet.deposit(self.amount)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.wallet:
            self.wallet.withdraw(self.amount)
        super().delete(*args, **kwargs)

    class Meta:
        db_table = "income"
        verbose_name = "Income"
        verbose_name_plural = "Incomes"