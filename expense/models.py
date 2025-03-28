from django.utils import timezone
from django.db import models, transaction

from django.db import models, transaction
from core.models_mixin import IdentifierTimeStampAbstractModel

class Expense(IdentifierTimeStampAbstractModel):
    """
    Expense model representing an expense record.
    Attributes:
        title (CharField): The title of the expense, optional.
        description (TextField): A detailed description of the expense, optional.
        amount (DecimalField): The amount of the expense.
        category (ForeignKey): The category of the expense, linked to ExpenseCategory, optional.
        user (ForeignKey): The user who made the expense, linked to CustomUser.
    Meta:
        db_table (str): The name of the database table.
        verbose_name (str): The human-readable name of the model.
        verbose_name_plural (str): The human-readable plural name of the model.
    Methods:
        __str__(): Returns a string representation of the expense, combining amount and category title.
    """
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey("core.ExpenseCategory", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='expense')
    date = models.DateField(default=timezone.now)
    wallet = models.ForeignKey("wallet.Wallet", on_delete=models.SET_NULL, null=True, related_name='expense')

    def clean(self):
        with transaction.atomic():
            if self.pk:
                # Existing instance, handle updates
                previous = Expense.objects.get(pk=self.pk)
                
                # Handle wallet change
                if previous.wallet and previous.wallet != self.wallet:
                    # Revert amount to previous wallet
                    previous.wallet.deposit(previous.amount)
                    
                    # Withdraw from new wallet if it exists
                    if self.wallet:
                        self.wallet.withdraw(self.amount)
                
                # Handle amount change for same wallet
                elif previous.wallet == self.wallet and self.wallet:
                    # Calculate the difference
                    difference = self.amount - previous.amount
                    self.wallet.withdraw(difference)
            else:
                # New instance, withdraw from wallet
                if self.wallet:
                    self.wallet.withdraw(self.amount)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.wallet:
            self.wallet.deposit(self.amount)
        super().delete(*args, **kwargs)

    class Meta:
        db_table = "expenses"
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"