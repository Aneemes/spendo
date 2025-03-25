from django.db import transaction
from decimal import Decimal
from uuid import UUID
from typing import List
from django.utils import timezone

from rest_framework.exceptions import ValidationError as DRFValidationError

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError

from core.models import ExpenseCategory
from account.models import CustomUser
from wallet.selectors import get_wallet_from_uid_and_user

from .models import Expense
from .selectors import get_expense_category_from_category_uid_and_user, get_expense_from_user_and_expense_uid

@transaction.atomic
def create_user_expense(
    *,
    title: str = None,
    description: str = None,
    amount: Decimal,
    category: UUID,
    wallet: UUID,
    date: str = None,
    user: CustomUser
) -> Expense:
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
    # this wont work gotta fix it later
    expense_category_instance = None
    if category:
        expense_category_instance = get_expense_category_from_category_uid_and_user(category_uid=category, user=user)
        if expense_category_instance is None:
            raise DRFValidationError(detail="Category not found.")
    
    wallet_instance = get_wallet_from_uid_and_user(wallet_uid=wallet, user=user)
    if wallet_instance is None:
        raise DRFValidationError(detail="Wallet not found.")
    
    if date is None:
        date = timezone.now().date()

    expense_instance = Expense(
        title=title,
        description=description,
        amount=amount,
        category=expense_category_instance,
        wallet=wallet_instance,
        date=date,
        user=user
    )
    
    try:
        expense_instance.full_clean()
        expense_instance.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(message=e.messages)
    
    return expense_instance


@transaction.atomic
def update_user_expense(
    *,
    title: str = None,
    description: str = None,
    amount: Decimal = None,
    category: UUID = None,
    user: CustomUser,
    wallet: UUID = None,
    expense_uid: UUID,
    date: str = None
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
    expense_instance = get_expense_from_user_and_expense_uid(user=user, expense_uid=expense_uid)
    if not expense_instance:
        raise DjangoValidationError("Expense not found.")
    
    if category:
        expense_category_instance = get_expense_category_from_category_uid_and_user(category_uid=category, user=user)
        if not expense_category_instance:
            raise DRFValidationError(detail="Category not found.")
        expense_instance.category = expense_category_instance
    
    if title:
        expense_instance.title = title
    
    if description:
        expense_instance.description = description
    
    if amount:
        expense_instance.amount = amount
    
    if date:
        expense_instance.date = date

    if wallet:
        wallet_instance = get_wallet_from_uid_and_user(wallet_uid=wallet, user=user)
        if not wallet_instance:
            raise DRFValidationError(detail="Wallet not found.")
    
        expense_instance.wallet = wallet_instance
    
    try:
        expense_instance.full_clean()
        expense_instance.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(message=e.messages)
    
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
    try:
        expense_instance = user.expense.get(uid=expense_uid)
    except ObjectDoesNotExist:
        raise DjangoValidationError("Expense not found.")
    expense_instance.delete()
    return True

