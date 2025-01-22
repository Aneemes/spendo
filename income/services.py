from decimal import Decimal
from uuid import UUID
from datetime import date

from account.models import CustomUser
from .models import Income, IncomeCategory
from .selectors import get_income_category_from_category_uid_and_user, get_income_from_user_and_income_uid

from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError

@transaction.atomic
def create_income(
    *,
    title: str = None,
    amount: Decimal,
    date: date,
    description: str = None,
    category_uid: UUID = None,
    user: CustomUser,
) -> Income:
    income_category_instance = None
    if category_uid:
        income_category_instance = get_income_category_from_category_uid_and_user(category_uid=category_uid, user=user)
        if income_category_instance is None:
            raise DRFValidationError(detail="Category not found.")

    income_instance = Income(
        title=title.strip() if title and title.strip() else None,
        amount=amount,
        date=date,
        description=description.strip() if description and description.strip() else None,
        category=income_category_instance,
        user=user,
    )

    try:
        income_instance.full_clean()
        income_instance.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(detail=e.messages[0])

    return income_instance

@transaction.atomic
def update_income(
    *,
    user: CustomUser,
    income_uid: UUID,
    title: str = None,
    amount: Decimal,
    date: date,
    description: str = None,
    category_uid: UUID = None,
) -> None:
    # Fetch the income instance for the given user and UID
    income_instance = get_income_from_user_and_income_uid(user=user, income_uid=income_uid)
    if not income_instance:
        raise DRFValidationError(detail="Income instance not found.")

    # Fetch the category instance if a category UID is provided
    if category_uid:
        income_category_instance = get_income_category_from_category_uid_and_user(category_uid=category_uid, user=user)
        if not income_category_instance:
            raise DRFValidationError(detail="Category not found.")
        income_instance.category = income_category_instance

    # Update fields if new values are provided
    if title:
        income_instance.title = title.strip() if title.strip() else None

    income_instance.amount = amount
    income_instance.date = date

    if description:
        income_instance.description = description.strip() if description.strip() else None

    try:
        income_instance.full_clean()
        income_instance.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])


@transaction.atomic
def delete_user_income(
    *,
    user: CustomUser,
    income_uid: UUID
) -> bool:
    income_instance = get_income_from_user_and_income_uid(user=user, income_uid=income_uid)
    if not income_instance:
        raise DRFValidationError(detail="Income instance not found.")
    income_instance.delete()
    return True

