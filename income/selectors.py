from uuid import UUID
from typing import Dict
from datetime import datetime, timedelta

from rest_framework.exceptions import ValidationError as DRFValidationError
from account.models import CustomUser
from .models import Income
from core.models import IncomeCategory

def get_income_category_from_category_uid_and_user(*, category_uid:UUID, user:CustomUser) -> IncomeCategory:
    try:
        income_category = IncomeCategory.objects.get(uid=category_uid, user=user)
    except IncomeCategory.DoesNotExist:
        return None
    return income_category

def get_income_from_user_and_income_uid(*, user:CustomUser, income_uid:UUID) -> Income:
    try:
        income = Income.objects.get(uid=income_uid, user=user)
    except Income.DoesNotExist:
        return None
    return income

def get_user_income_details(*, user: CustomUser, income_uid: UUID) -> Dict:

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