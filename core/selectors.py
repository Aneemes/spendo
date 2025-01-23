from typing import List
from core.models import ExpenseCategory, IncomeCategory
from account.models import CustomUser
from uuid import UUID

def fetch_expense_categories(
    *,
    user: CustomUser
) -> List[ExpenseCategory]:
    """
    Fetches the expense categories associated with a given user.
    Args:
        user (CustomUser): The user whose expense categories are to be fetched.
    Returns:
        List[ExpenseCategory]: A list of expense categories associated with the user.
    """
    try:
        categories = ExpenseCategory.objects.filter(user=user)
    except ExpenseCategory.DoesNotExist:
        return None
    return categories

def fetch_expense_category_detail(
    *,
    category_uid: UUID,
    user: CustomUser
) -> ExpenseCategory:
    """
    Fetches the details of an expense category for a given user.
    Args:
        category_uid (UUID): The unique identifier of the expense category.
        user (CustomUser): The user for whom the expense category is being fetched.
    Returns:
        ExpenseCategory: The expense category object corresponding to the given UID and user.
    Raises:
        ExpenseCategory.DoesNotExist: If no expense category exists with the given UID for the specified user.
    """
    try:
        category = ExpenseCategory.objects.get(uid=category_uid, user=user)
    except ExpenseCategory.DoesNotExist:
        return None
    return category

def fetch_income_categories(
    *,
    user: CustomUser
) -> List[IncomeCategory]:
    """
    Fetches the income categories associated with a given user.
    Args:
        user (CustomUser): The user whose income categories are to be fetched.
    Returns:
        List[IncomeCategory]: A list of income categories associated with the user.
    """
    try:
        categories = IncomeCategory.objects.filter(user=user)
    except IncomeCategory.DoesNotExist:
        return None
    return categories

def fetch_income_category_detail(
    *,
    category_uid: UUID,
    user: CustomUser
) -> IncomeCategory:
    """
    Fetches the details of an income category for a given user.
    Args:
        category_uid (UUID): The unique identifier of the income category.
        user (CustomUser): The user for whom the income category is being fetched.
    Returns:
        IncomeCategory: The income category object corresponding to the given UID and user.
    Raises:
        IncomeCategory.DoesNotExist: If no income category exists with the given UID for the specified user.
    """
    try:
        category = IncomeCategory.objects.get(uid=category_uid, user=user)
    except IncomeCategory.DoesNotExist:
        return None
    return category