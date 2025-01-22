from django.db import models
from core.models_mixin import IdentifierTimeStampAbstractModel
from core.models import IncomeCategory

class Income(IdentifierTimeStampAbstractModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("core.IncomeCategory", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='income')

    class Meta:
        db_table = "income"
        verbose_name = "Income"
        verbose_name_plural = "Incomes"