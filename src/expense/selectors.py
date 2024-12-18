from typing import Dict
from datetime import datetime, timedelta
from uuid import UUID
from .models import Expense
from account.models import CustomUser
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
    # Start with all the user's expenses
    expense_list = user.expense_set.select_related('category')

    # Filter by title if provided
    if title:
        expense_list = expense_list.filter(title__icontains=title)

    # Date range filter
    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")  # Ensure the date format is YYYY-MM-DD
            expense_list = expense_list.filter(created_at__gte=start_date)
        except ValueError:
            raise DjangoValidationError("Invalid start_date format. Expected YYYY-MM-DD.")
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")  # Ensure the date format is YYYY-MM-DD
            expense_list = expense_list.filter(created_at__lte=end_date)
        except ValueError:
            raise DjangoValidationError("Invalid end_date format. Expected YYYY-MM-DD.")

    # Handle the predefined date filters
    if date_filter:
        today = datetime.today()
        if date_filter == "today":
            expense_list = expense_list.filter(created_at__date=today.date())
        elif date_filter == "yesterday":
            yesterday = today - timedelta(days=1)
            expense_list = expense_list.filter(created_at__date=yesterday.date())
        elif date_filter == "last_7_days":
            seven_days_ago = today - timedelta(days=7)
            expense_list = expense_list.filter(created_at__gte=seven_days_ago)
        elif date_filter == "last_15_days":
            fifteen_days_ago = today - timedelta(days=15)
            expense_list = expense_list.filter(created_at__gte=fifteen_days_ago)
        elif date_filter == "last_30_days":
            thirty_days_ago = today - timedelta(days=30)
            expense_list = expense_list.filter(created_at__gte=thirty_days_ago)
        elif date_filter == "last_90_days":
            ninety_days_ago = today - timedelta(days=90)
            expense_list = expense_list.filter(created_at__gte=ninety_days_ago)
        elif date_filter == "last_365_days":
            one_year_ago = today - timedelta(days=365)
            expense_list = expense_list.filter(created_at__gte=one_year_ago)
        else:
            raise DjangoValidationError("Invalid date_filter value. Valid options are 'today', 'yesterday', 'last_7_days', 'last_15_days', 'last_30_days', 'last_90_days', 'last_365_days'.")

    # Filter by category if provided
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
        expense_instance = user.expense_set.get(uid=expense_uid)
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