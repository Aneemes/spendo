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

    # this should theoretically work but idk lmao
    def clean(self):
        if self.pk:
            # Existing instance, handle updates
            previous = Income.objects.get(pk=self.pk)
            if previous.wallet and previous.wallet != self.wallet:
                # Revert the amount from the previous wallet
                previous.wallet.balance -= previous.amount
                previous.wallet.save()
            if previous.wallet == self.wallet:
                # Adjust the balance if the amount has changed
                self.wallet.balance += self.amount - previous.amount
            else:
                # Add the amount to the new wallet
                if self.wallet:
                    self.wallet.balance += self.amount
            if previous.wallet and previous.wallet != self.wallet:
                previous.wallet.save()
        else:
            # New instance, handle creation
            if self.wallet:
                self.wallet.balance += self.amount
                self.wallet.save()

    # this should work too idk lmao
    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.wallet:
            self.wallet.balance -= self.amount
            self.wallet.save()
        super().delete(*args, **kwargs)

    class Meta:
        db_table = "income"
        verbose_name = "Income"
        verbose_name_plural = "Incomes"