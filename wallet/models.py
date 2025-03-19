from django.db import models
from core.models_mixin import IdentifierTimeStampAbstractModel

class Wallet(IdentifierTimeStampAbstractModel):
    title = models.CharField(max_length=125)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='wallet')
    color = models.CharField(max_length=7, default="#007bff")
    
    class Meta:
        db_table="user_wallet"
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"
        unique_together = ('title', 'user')
    

