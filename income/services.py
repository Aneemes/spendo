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
    """
    Create a new income record with the provided details.
    This function creates and saves a new Income instance with the given parameters.
    The function is wrapped in a database transaction to ensure atomicity.
    Args:
        title (str, optional): The title of the income. Will be stripped of whitespace.
            Defaults to None.
        amount (Decimal): The monetary amount of the income.
        date (date): The date when the income was received.
        description (str, optional): Additional details about the income. Will be stripped
            of whitespace. Defaults to None.
        category_uid (UUID, optional): The unique identifier of the income category.
            Defaults to None.
        user (CustomUser): The user who owns this income record.
    Returns:
        Income: The newly created and saved income instance.
    Raises:
        DRFValidationError: If the specified category is not found.
        DjangoValidationError: If the income data fails model validation.
    """
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
    """
    Updates an existing income record for a user.
    This function updates the specified income instance with new values while maintaining data integrity
    through atomic transaction.
    Args:
        user (CustomUser): The user who owns the income record.
        income_uid (UUID): The unique identifier of the income record to update.
        title (str, optional): New title for the income record. Defaults to None.
        amount (Decimal): New amount for the income record.
        date (date): New date for the income record.
        description (str, optional): New description for the income record. Defaults to None.
        category_uid (UUID, optional): The unique identifier of the new category. Defaults to None.
    Raises:
        DRFValidationError: If the income instance or category is not found.
        DjangoValidationError: If the updated data fails model validation.
    Returns:
        None
    """
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
    """
    Delete user income instance.
    This function deletes an income instance associated with a specific user. The operation is
    executed within a database transaction to ensure data consistency.

    Args:
        user (CustomUser): The user whose income is to be deleted
        income_uid (UUID): Unique identifier of the income to be deleted

    Returns:
        bool: True if deletion was successful

    Raises:
        DRFValidationError: If income instance is not found for the given user and income_uid

    Example:
        >>> delete_user_income(user=current_user, income_uid=uuid4())
        True
    """
    income_instance = get_income_from_user_and_income_uid(user=user, income_uid=income_uid)
    if not income_instance:
        raise DRFValidationError(detail="Income instance not found.")
    income_instance.delete()
    return True

