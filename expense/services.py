from django.db import transaction
from decimal import Decimal
from uuid import UUID
from typing import List
from core.models import ExpenseCategory
from account.models import CustomUser
from django.core.exceptions import ValidationError as DjangoValidationError

@transaction.atomic
def create_user_expense(
    *,
    title: str = None,
    description: str = None,
    amount: Decimal,
    category: UUID,
    user: CustomUser
) -> bool:
    """
    Creates a new user expense entry in the specified category.

    Args:
        title (str, optional): The title of the expense. Defaults to None.
        description (str, optional): A description of the expense. Defaults to None.
        amount (Decimal): The amount of the expense.
        category (UUID): The unique identifier of the expense category.
        user (CustomUser): The user who is creating the expense.

    Returns:
        bool: True if the expense was successfully created.

    Raises:
        DjangoValidationError: If the specified category is not found for the user.
    """
    category_instance = ExpenseCategory.objects.get(uid=category, user=user)
    if category_instance is None:
        raise DjangoValidationError("Category not found")
    user_expense = category_instance.expense_set.create(
        title=title,
        description=description,
        amount=amount,
        user=user
    )
    return True


@transaction.atomic
def update_user_expense(
    *,
    title: str = None,
    description: str = None,
    amount: Decimal = None,
    category: UUID = None,
    user: CustomUser,
    expense_uid: UUID
) -> bool:
    """
    Updates an existing expense for a user with the provided details.
    Args:
        title (str, optional): The new title for the expense. Defaults to None.
        description (str, optional): The new description for the expense. Defaults to None.
        amount (Decimal, optional): The new amount for the expense. Defaults to None.
        category (UUID, optional): The UUID of the new category for the expense. Defaults to None.
        user (CustomUser): The user who owns the expense.
        expense_uid (UUID): The UUID of the expense to be updated.
    Raises:
        DjangoValidationError: If the expense or category is not found, or if validation fails.
    Returns:
        bool: True if the expense was successfully updated.
    """
    expense_instance = user.expense_set.get(uid=expense_uid)
    if expense_instance is None:
        raise DjangoValidationError("Expense not found")
    if title is not None:
        expense_instance.title = title
    if description is not None:
        expense_instance.description = description
    if amount is not None:
        expense_instance.amount = amount
    if category is not None:
        category_instance = ExpenseCategory.objects.get(uid=category, user=user)
        if category_instance is None:
            raise DjangoValidationError("Category not found")
        expense_instance.category = category_instance

    try:
        expense_instance.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])

    expense_instance.save()
    return True

@transaction.atomic
def delete_user_expense(
    *,
    user: CustomUser,
    expense_uid: UUID
) -> bool:
    """
    Deletes a user's expense based on the provided expense UID.

    Args:
        user (CustomUser): The user whose expense is to be deleted.
        expense_uid (UUID): The unique identifier of the expense to be deleted.

    Returns:
        bool: True if the expense was successfully deleted.

    Raises:
        DjangoValidationError: If the expense with the given UID is not found.
    """
    expense_instance = user.expense_set.get(uid=expense_uid)
    if expense_instance is None:
        raise DjangoValidationError("Expense not found")
    expense_instance.delete()
    return True

