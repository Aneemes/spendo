from uuid import UUID
from typing import Dict
from datetime import datetime, timedelta

from rest_framework.exceptions import ValidationError as DRFValidationError
from account.models import CustomUser
from .models import Income
from core.models import IncomeCategory

def get_income_category_from_category_uid_and_user(*, category_uid:UUID, user:CustomUser) -> IncomeCategory:
    """
    Retrieve an IncomeCategory instance based on category UID and user.

    Args:
        category_uid (UUID): The unique identifier of the income category
        user (CustomUser): The user associated with the income category

    Returns:
        IncomeCategory: The matching income category if found
        None: If no matching income category exists

    Examples:
        >>> category = get_income_category_from_category_uid_and_user(
        ...     category_uid=uuid.UUID('12345678-1234-5678-1234-567812345678'),
        ...     user=current_user
        ... )
        >>> if category:
        ...     print(category.name)
        ... else:
        ...     print("Category not found")
    """
    try:
        income_category = IncomeCategory.objects.get(uid=category_uid, user=user)
    except IncomeCategory.DoesNotExist:
        return None
    return income_category

def get_income_from_user_and_income_uid(*, user:CustomUser, income_uid:UUID) -> Income:
    """
    Retrieve an Income object based on user and income UUID.

    This function attempts to fetch a single Income record from the database that matches both
    the provided user and income UUID. If no matching record is found, returns None.

    Args:
        user (CustomUser): The user associated with the income record
        income_uid (UUID): The unique identifier of the income record to retrieve

    Returns:
        Income: The matching Income object if found
        None: If no matching record exists

    Raises:
        None: Exception is caught internally and returns None
    """
    try:
        income = Income.objects.get(uid=income_uid, user=user)
    except Income.DoesNotExist:
        return None
    return income

def get_user_income_details(*, user: CustomUser, income_uid: UUID) -> Dict:
    """
    Retrieve detailed information about a specific income record for a given user.
    Args:
        user (CustomUser): The user whose income details are being retrieved.
        income_uid (UUID): The unique identifier of the income record.
    Returns:
        Dict: A dictionary containing income details with the following keys:
            - uid: UUID of the income record
            - title: Title of the income
            - description: Description of the income
            - date: Date of the income
            - amount: Amount of the income
            - category: UUID of the income category
            - category_title: Title of the income category
            - color_code: Color code of the income category
    Raises:
        DRFValidationError: If the income record with the specified UUID is not found.
    """

    try:
        income_instance = user.income_set.get(uid=income_uid)
    except Income.DoesNotExist:
        raise DRFValidationError(detail="Income not found.")
    income_details = {
        "uid": income_instance.uid,
        "title": income_instance.title,
        "description": income_instance.description,
        "date": income_instance.date,
        "amount": income_instance.amount,
        "category": income_instance.category.uid,
        "category_title": income_instance.category.title,
        "color_code": income_instance.category.color_code
    }
    return income_details


def get_user_income_list(
    *, user: CustomUser, 
    title: str = None, 
    start_date: str = None, 
    end_date: str = None, 
    category_uid: str = None, 
    date_filter: str = None
) -> Dict:
    """
    Retrieves a filtered list of income records for a specific user.
    This function allows filtering of income records based on various criteria such as title,
    date range, predefined date filters, and category.
    Args:
        user (CustomUser): The user whose income records are to be retrieved.
        title (str, optional): Filter income records by title (case-insensitive partial match).
        start_date (str, optional): Start date for date range filter (format: YYYY-MM-DD).
        end_date (str, optional): End date for date range filter (format: YYYY-MM-DD).
        category_uid (str, optional): Filter income records by category UUID.
        date_filter (str, optional): Predefined date filter. Valid options are:
            - 'today': Records from current day
            - 'yesterday': Records from previous day
            - 'last_7_days': Records from last 7 days
            - 'last_15_days': Records from last 15 days
            - 'last_30_days': Records from last 30 days
            - 'last_90_days': Records from last 90 days
            - 'last_365_days': Records from last 365 days
    Returns:
        Dict: A queryset of filtered income records.
    Raises:
        DRFValidationError: If the date format is invalid or if an invalid date_filter value is provided.
    """
    # Start with all the user's income
    income_list = user.income_set.select_related('category')

    # Filter by title if provided
    if title:
        income_list = income_list.filter(title__icontains=title)

    # Date range filter
    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")  # Ensure the date format is YYYY-MM-DD
            income_list = income_list.filter(date_gte=start_date)
        except ValueError:
            raise DRFValidationError(detail="Invalid start_date format. Expected YYYY-MM-DD.")
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")  # Ensure the date format is YYYY-MM-DD
            income_list = income_list.filter(date_lte=end_date)
        except ValueError:
            raise DRFValidationError(detail="Invalid end_date format. Expected YYYY-MM-DD.")

    # Handle the predefined date filters
    # temporary shit will clean this up later and same cleanup required for expense list
    if date_filter:
        today = datetime.today()
        if date_filter == "today":
            income_list = income_list.filter(date=today.date())
        elif date_filter == "yesterday":
            yesterday = today - timedelta(days=1)
            income_list = income_list.filter(date=yesterday.date())
        elif date_filter == "last_7_days":
            seven_days_ago = today - timedelta(days=7)
            income_list = income_list.filter(date=seven_days_ago)
        elif date_filter == "last_15_days":
            fifteen_days_ago = today - timedelta(days=15)
            income_list = income_list.filter(date=fifteen_days_ago)
        elif date_filter == "last_30_days":
            thirty_days_ago = today - timedelta(days=30)
            income_list = income_list.filter(date=thirty_days_ago)
        elif date_filter == "last_90_days":
            ninety_days_ago = today - timedelta(days=90)
            income_list = income_list.filter(date=ninety_days_ago)
        elif date_filter == "last_365_days":
            one_year_ago = today - timedelta(days=365)
            income_list = income_list.filter(date=one_year_ago)
        else:
            raise DRFValidationError(detail="Invalid date_filter value. Valid options are 'today', 'yesterday', 'last_7_days', 'last_15_days', 'last_30_days', 'last_90_days', 'last_365_days'.")

    # Filter by category if provided
    if category_uid:
        income_list = income_list.filter(category__uid=category_uid)

    return income_list