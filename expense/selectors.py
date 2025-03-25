from typing import Dict
from datetime import datetime, timedelta
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError

from core.models import ExpenseCategory
from account.models import CustomUser

from .models import Expense
from django.core.exceptions import ValidationError as DjangoValidationError

def get_user_expense_list(
    *, user: CustomUser, 
    title: str = None, 
    start_date: str = None, 
    end_date: str = None, 
    category_uid: str = None, 
    date_filter: str = None
) -> Dict:
    """
    Retrieve a list of user expenses with optional filters.
    Args:
        user (CustomUser): The user whose expenses are to be retrieved.
        title (str, optional): Filter expenses by title containing this string. Defaults to None.
        start_date (str, optional): Filter expenses created on or after this date (YYYY-MM-DD). Defaults to None.
        end_date (str, optional): Filter expenses created on or before this date (YYYY-MM-DD). Defaults to None.
        category_uid (str, optional): Filter expenses by category UID. Defaults to None.
        date_filter (str, optional): Predefined date filter. Valid options are 'today', 'yesterday', 'last_7_days', 'last_15_days', 'last_30_days', 'last_90_days', 'last_365_days'. Defaults to None.
    Returns:
        Dict: A dictionary of filtered user expenses.
    Raises:
        DjangoValidationError: If the date format for start_date or end_date is invalid.
        DjangoValidationError: If the date_filter value is invalid.
    """
    expense_list = user.expense.select_related('category')

    if title:
        expense_list = expense_list.filter(title__icontains=title)

    date_filters = {
        "today": datetime.today().date(),
        "yesterday": (datetime.today() - timedelta(days=1)).date(),
        "last_7_days": datetime.today() - timedelta(days=7),
        "last_15_days": datetime.today() - timedelta(days=15),
        "last_30_days": datetime.today() - timedelta(days=30),
        "last_90_days": datetime.today() - timedelta(days=90),
        "last_365_days": datetime.today() - timedelta(days=365),
    }

    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            expense_list = expense_list.filter(created_at__gte=start_date)
        except ValueError:
            raise DjangoValidationError("Invalid start_date format. Expected YYYY-MM-DD.")
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            expense_list = expense_list.filter(created_at__lte=end_date)
        except ValueError:
            raise DjangoValidationError("Invalid end_date format. Expected YYYY-MM-DD.")

    if date_filter:
        if date_filter in date_filters:
            filter_date = date_filters[date_filter]
            if isinstance(filter_date, datetime):
                expense_list = expense_list.filter(created_at__gte=filter_date)
            else:
                expense_list = expense_list.filter(created_at__date=filter_date)
        else:
            raise DjangoValidationError("Invalid date_filter value. Valid options are 'today', 'yesterday', 'last_7_days', 'last_15_days', 'last_30_days', 'last_90_days', 'last_365_days'.")

    if category_uid:
        expense_list = expense_list.filter(category__uid=category_uid)

    return expense_list

def get_user_expense_details(*, user: CustomUser, expense_uid: UUID) -> Dict:
    """
    Retrieve the details of a specific expense for a given user.

    Args:
        user (CustomUser): The user whose expense details are to be retrieved.
        expense_uid (UUID): The unique identifier of the expense.

    Returns:
        Dict: A dictionary containing the details of the expense, including:
            - uid (UUID): The unique identifier of the expense.
            - title (str): The title of the expense.
            - description (str): The description of the expense.
            - amount (Decimal): The amount of the expense.
            - category (UUID): The unique identifier of the expense category.
            - category_title (str): The title of the expense category.
            - color_code (str): The color code associated with the expense category.

    Raises:
        DjangoValidationError: If the expense with the given UID does not exist.
    """
    try:
        expense_instance = user.expense.get(uid=expense_uid)
    except Expense.DoesNotExist:
        raise DjangoValidationError("Expense not found")
    expense_details = {
        "uid": expense_instance.uid,
        "title": expense_instance.title,
        "description": expense_instance.description,
        "amount": expense_instance.amount,
        "category": expense_instance.category.uid,
        "category_title": expense_instance.category.title,
        "color_code": expense_instance.category.color_code
    }
    return expense_details

def get_expense_category_from_category_uid_and_user(*, category_uid: UUID, user: CustomUser):
    """
    Retrieve an expense category instance based on the category UID and user.

    Args:
        category_uid (UUID): The unique identifier of the expense category.
        user (CustomUser): The user who owns the expense category.

    Returns:
        ExpenseCategory: The expense category instance.

    Raises:
        DjangoValidationError: If the expense category with the given UID is not found.
    """
    try:
        category_instance = user.expensecategory_set.get(uid=category_uid)
    except ExpenseCategory.DoesNotExist:
        raise DjangoValidationError("Category not found")
    return category_instance

def get_expense_from_user_and_expense_uid(*, user: CustomUser, expense_uid: UUID):
    """
    Retrieve an expense instance based on the expense UID and user.

    Args:
        user (CustomUser): The user who owns the expense.
        expense_uid (UUID): The unique identifier of the expense.

    Returns:
        Expense: The expense instance.

    Raises:
        DjangoValidationError: If the expense with the given UID is not found.
    """
    try:
        expense_instance = user.expense.get(uid=expense_uid)
    except Expense.DoesNotExist:
        raise DjangoValidationError("Expense not found")
    return expense_instance