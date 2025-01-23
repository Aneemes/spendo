from django.db import transaction
from uuid import UUID
from core.models import ExpenseCategory, IncomeCategory
from account.models import CustomUser
from django.core.exceptions import ValidationError as DjangoValidationError

@transaction.atomic
def create_expense_category(
    *,
    title: str,
    description: str = None,
    color_code: str = '#000000',
    user: CustomUser
) -> ExpenseCategory:
    """
    Creates a new expense category for a user.

    Args:
        title (str): The title of the expense category.
        description (str, optional): A description of the expense category. Defaults to None.
        color_code (str, optional): The color code associated with the expense category. Defaults to '#000000'.
        user (CustomUser): The user to whom the expense category belongs.

    Returns:
        ExpenseCategory: The created expense category instance.

    Raises:
        DjangoValidationError: If the expense category instance fails validation.
    """
    category_instance = ExpenseCategory(
        title=title,
        description=description,
            color_code=color_code,
        user=user
    )
    try:
        category_instance.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    category_instance.save()
    return category_instance

@transaction.atomic
def update_expense_category(
    *,
    category_uid: UUID,
    title: str = None,
    description: str = None,
    color_code: str = None,
    user: CustomUser
) -> ExpenseCategory:
    """
    Updates an existing expense category with the provided details.
    Args:
        category_uid (UUID): The unique identifier of the category to update.
        title (str, optional): The new title for the category. Defaults to None.
        description (str, optional): The new description for the category. Defaults to None.
        color_code (str, optional): The new color code for the category. Defaults to None.
        user (CustomUser): The user who owns the category.
    Returns:
        ExpenseCategory: The updated expense category.
    Raises:
        DjangoValidationError: If the category is not found or if validation fails.
    """
    try:
        category = ExpenseCategory.objects.get(uid=category_uid, user=user)
    except ExpenseCategory.DoesNotExist:
        raise DjangoValidationError("Category not found.")

    if title is not None:
        category.title = title
    if description is not None:
        category.description = description
    if color_code is not None:
        category.color_code = color_code
    try:
        category.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    category.save()
    return category

@transaction.atomic
def delete_expense_category(
    *,
    category_uid: UUID,
    user: CustomUser
) -> bool:
    """
    Deletes an expense category for a given user.

    Args:
        category_uid (UUID): The unique identifier of the expense category to be deleted.
        user (CustomUser): The user who owns the expense category.

    Returns:
        bool: True if the expense category was successfully deleted.

    Raises:
        DjangoValidationError: If the expense category does not exist.
    """
    try:
        category_instance = ExpenseCategory.objects.get(uid=category_uid, user=user)
    except ExpenseCategory.DoesNotExist:
        raise DjangoValidationError("Category not found")
    category_instance.delete()
    return True


@transaction.atomic
def create_income_category(
    *,
    title: str,
    description: str = None,
    color_code: str = '#000000',
    user: CustomUser
) -> IncomeCategory:
    """
    Creates a new income category for a user.

    Args:
        title (str): The title of the income category.
        description (str, optional): A description of the income category. Defaults to None.
        color_code (str, optional): The color code associated with the income category. Defaults to '#000000'.
        user (CustomUser): The user to whom the income category belongs.

    Returns:
        IncomeCategory: The created income category instance.

    Raises:
        DjangoValidationError: If the income category instance fails validation.
    """
    category_instance = IncomeCategory(
        title=title,
        description=description,
            color_code=color_code,
        user=user
    )
    try:
        category_instance.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    category_instance.save()
    return category_instance

@transaction.atomic
def update_income_category(
    *,
    category_uid: UUID,
    title: str = None,
    description: str = None,
    color_code: str = None,
    user: CustomUser
) -> IncomeCategory:
    """
    Updates an existing income category with the provided details.
    Args:
        category_uid (UUID): The unique identifier of the category to update.
        title (str, optional): The new title for the category. Defaults to None.
        description (str, optional): The new description for the category. Defaults to None.
        color_code (str, optional): The new color code for the category. Defaults to None.
        user (CustomUser): The user who owns the category.
    Returns:
        IncomeCategory: The updated income category.
    Raises:
        DjangoValidationError: If the category is not found or if validation fails.
    """
    try:
        category = IncomeCategory.objects.get(uid=category_uid, user=user)
    except IncomeCategory.DoesNotExist:
        raise DjangoValidationError("Category not found.")

    if title is not None:
        category.title = title
    if description is not None:
        category.description = description
    if color_code is not None:
        category.color_code = color_code
    try:
        category.full_clean()
        category.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    return category

@transaction.atomic
def delete_income_category(
    *,
    category_uid: UUID,
    user: CustomUser
) -> bool:
    """
    Deletes an income category for a given user.

    Args:
        category_uid (UUID): The unique identifier of the income category to be deleted.
        user (CustomUser): The user who owns the income category.

    Returns:
        bool: True if the income category was successfully deleted.

    Raises:
        DjangoValidationError: If the income category does not exist.
    """
    try:
        category_instance = IncomeCategory.objects.get(uid=category_uid, user=user)
    except IncomeCategory.DoesNotExist:
        raise DjangoValidationError("Category not found.")
    category_instance.delete()
    return True