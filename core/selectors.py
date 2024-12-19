from typing import List
from core.models import ExpenseCategory
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
    
    categories = ExpenseCategory.objects.filter(user=user)
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
    
    category = ExpenseCategory.objects.get(uid=category_uid, user=user)
    return category
