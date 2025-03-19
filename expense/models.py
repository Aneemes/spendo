from django.utils import timezone

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
        if self.pk:
            # Existing instance, handle updates
            previous = Expense.objects.get(pk=self.pk)
            if previous.wallet and previous.wallet != self.wallet:
                # Revert the amount from the previous wallet
                previous.wallet.balance += previous.amount
                previous.wallet.save()
            if previous.wallet == self.wallet:
                # Adjust the balance if the amount has changed
                self.wallet.balance -= self.amount - previous.amount
            else:
                # Subtract the amount from the new wallet
                if self.wallet:
                    self.wallet.balance -= self.amount
            if previous.wallet and previous.wallet != self.wallet:
                previous.wallet.save()
        else:
            # New instance, handle creation
            if self.wallet:
                self.wallet.balance -= self.amount
                self.wallet.save()

    def save(self, *args, **kwargs):
        self.full_clean()  # This will call the clean method
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.wallet:
            self.wallet.balance += self.amount
            self.wallet.save()
        super().delete(*args, **kwargs)

    class Meta:
        db_table = "expenses"
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
