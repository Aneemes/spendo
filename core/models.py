from django.db import models
from .models_mixin import IdentifierTimeStampAbstractModel

class ExpenseCategory(IdentifierTimeStampAbstractModel):
    """
    ExpenseCategory model represents a category for expenses.
    Attributes:
        title (CharField): The title of the expense category with a maximum length of 255 characters.
        description (TextField): An optional description of the expense category.
        color_code (CharField): The color code associated with the expense category, default is "#000000".
        user (ForeignKey): A foreign key reference to the CustomUser model, indicating the user who owns this category.
    Meta:
        db_table (str): The name of the database table.
        verbose_name (str): The human-readable name of the model in singular form.
        verbose_name_plural (str): The human-readable name of the model in plural form.
        unique_together (tuple): Ensures that the combination of title and user is unique.
    Methods:
        __str__(): Returns the string representation of the expense category, which is the title.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=10, default="#000000")
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE)

    class Meta:
        db_table = "expense_categories"
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"
        unique_together = ('title', 'user')

    def __str__(self):
        return self.title

class IncomeCategory(IdentifierTimeStampAbstractModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=10, default="#000000")
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE)

    class Meta:
        db_table = "income_category"
        verbose_name = "Income Category"
        verbose_name_plural = "Income Categories"
        unique_together = ('title', 'user')

    def __str__(self):
        return self.title