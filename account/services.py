from dataclasses import dataclass

from django.db import transaction
from django.utils.crypto import get_random_string
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import CustomUser, EmailConfirmationToken
from .helpers import check_if_email_is_taken, send_reset_password_link, generate_username_from_email, send_verification_email

@transaction.atomic
def user_signup(
    *,
    full_name: str,
    email: str,
    password: str,
    confirm_password: str
) -> bool:
    """
    Registers a new user with the provided details.
    Args:
        full_name (str): The full name of the user.
        email (str): The email address of the user.
        password (str): The password for the user account.
        confirm_password (str): The confirmation of the password.
    Returns:
        tuple: A tuple containing UserSignupDetails and refresh token.
    Raises:
        DjangoValidationError: If any validation error occurs during the signup process.
    """
    if not password or not confirm_password:
        raise DjangoValidationError("Password field cannot be empty.")
    
    if password != confirm_password:
        raise DjangoValidationError("Password and Confirm password fields do not match.")
    
    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    
    existing_user = check_if_email_is_taken(email=email.lower())
    if existing_user:
        raise DjangoValidationError("User with that email address already exists.")
    
    username = generate_username_from_email(email=email.lower())
    
    user = CustomUser(
        full_name=full_name,
        username=username,
        email=email.lower(),
        is_active=False
    )

    try:
        user.set_password(password)
        user.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    user.save()

    send_verification_email(user=user, email=email)

    return True

@transaction.atomic
def user_login(
    *,
    email:str,
    password:str
) -> tuple:
    """
    Authenticates a user using their email and password.
    Args:
        email (str): The email address of the user.
        password (str): The password of the user.
    Returns:
        tuple: A tuple containing:
            - UserLoginDetails: A dataclass instance with the user's full name, username, and access token.
            - str: The refresh token.
    Raises:
        DjangoValidationError: If the email does not correspond to any user or if the password is incorrect.
    """
    @dataclass(frozen=True)
    class UserLoginDetails:
        full_name: str
        username: str

    try:
        user = CustomUser.objects.get(email=email.lower())
    except CustomUser.DoesNotExist:
        raise DRFValidationError(detail="User with the provided email does not exist.")
    
    if not user.check_password(password):
        raise DRFValidationError(detail="Invalid credentials.")
    
    if not user.is_active:
        raise DRFValidationError(detail="Please verify your email address before logging in.")
    
    full_name = user.full_name
    username = user.username


    token = RefreshToken.for_user(user)
    access_token = str(token.access_token)
    refresh_token = str(token)

    login_details = UserLoginDetails(
        full_name, username
    )

    return login_details, refresh_token, access_token

@transaction.atomic
def send_forgot_password_email(
    *,
    email:str
) -> bool:
    """
    Sends a forgot password email to the user with the given email address.
    This function generates a random token, updates the user's password with the token,
    and sends a reset password link to the user's email address.
    Args:
        email (str): The email address of the user who forgot their password.
    Returns:
        bool: True if the email was sent successfully, otherwise raises an exception.
    Raises:
        DjangoValidationError: If the email address is not associated with any user.
        APIException: If there is an error sending the email.
    """
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        raise DRFValidationError(detail="User with the provided email does not exist.")
    if user is None:
        raise DjangoValidationError("Please enter a valid email address.")
    token = get_random_string(length=64)
    user.password = token
    user.save()

    username = user.username

    reset_link = f"https://aneemes.pythonanywhere.com/auth/reset-password/{username}/{token}"
    email = send_reset_password_link(reset_link=reset_link, receiver_email=email, user=user)
    if email is True:
        return True
    
    raise APIException("There was some error at our end, please try again later")

@transaction.atomic
def reset_password(
    *,
    username: str,
    token: str,
    password: str,
    confirm_password: str
) -> bool:
    """
    Resets the password for a user.
    Args:
        username (str): The username of the user whose password is to be reset.
        token (str): The token to validate the password reset request.
        password (str): The new password.
        confirm_password (str): The confirmation of the new password.
    Returns:
        bool: True if the password was successfully reset, False otherwise.
    Raises:
        DjangoValidationError: If the user does not exist.
        DjangoValidationError: If the token is invalid.
        DjangoValidationError: If the password or confirm password is empty.
        DjangoValidationError: If the password and confirm password do not match.
        DjangoValidationError: If the password does not meet validation criteria.
        DjangoValidationError: If there is an error during saving the user.
    """
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        raise DjangoValidationError("User doesn't exist.")
    if user.password != token:
        raise DjangoValidationError("Invalid token.")
    if password is None or confirm_password is None:
        raise DjangoValidationError("Password should not be empty.")
    if password != confirm_password:
        raise DjangoValidationError("Password and confirm password did not match.")
    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    try:
        user.set_password(password)
        user.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    user.save()

    return True

@transaction.atomic
def change_password(
    *,
    user: CustomUser,
    old_password: str,
    new_password: str,
    confirm_password: str
) -> bool:
    """
    Change the password for a given user.
    Args:
        user (CustomUser): The user whose password is to be changed.
        old_password (str): The current password of the user.
        new_password (str): The new password to set.
        confirm_password (str): Confirmation of the new password.
    Returns:
        bool: True if the password was successfully changed, False otherwise.
    Raises:
        DjangoValidationError: If the new password and confirm password do not match.
        DjangoValidationError: If the old password is incorrect.
        DjangoValidationError: If the new password does not meet validation criteria.
        DjangoValidationError: If there is an error during saving the new password.
    """
    
    if new_password != confirm_password:
        raise DjangoValidationError("New password and Confirm new password do not match.")
    
    if not user.check_password(password=old_password):
        raise DjangoValidationError("Old password is incorrect.")
    
    try:
        validate_password(new_password)
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    
    try:
        user.set_password(new_password)
        user.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    
    user.save()
    return True

@transaction.atomic
def verify_user_email_address(*, token:str) -> bool:
    """
    Verifies a user's email address using a confirmation token.
    This function validates the email confirmation token, checks for expiration,
    and activates the associated user account if valid.
    Args:
        token (str): The email confirmation token string.
    Returns:
        bool: True if verification is successful.
    Raises:
        DRFValidationError: If token is invalid or expired.
        EmailConfirmationToken.DoesNotExist: If token not found.
    """
    try:
        token_object = EmailConfirmationToken.objects.get(token=token)
    except EmailConfirmationToken.DoesNotExist:
        raise DRFValidationError(detail='Email confirmation link is invalid.')
    if token_object.has_expired:
        token_object.delete()
        raise DRFValidationError(detail='Confirmation email has expired. Please request a new confirmation email.')
    
    user_instance = token_object.user
    user_instance.is_active=True
    user_instance.save(update_fields=['is_active'])

    token_object.delete()

    return True

@transaction.atomic
def resend_verification_email(*, email:str) -> bool:
    """
    Resends verification email to the specified email address.

    This function handles the process of resending a verification email to users who haven't
    verified their email address yet. It checks if the user exists, if they're already
    verified, and manages the verification token before sending a new email.

    Args:
        email (str): The email address to resend verification to.

    Returns:
        bool: True if the email was sent successfully or if the user doesn't exist.

    Raises:
        DRFValidationError: If the user's email is already verified.

    Example:
        >>> resend_verification_email(email="user@example.com")
        True
    """
    try:
        user_obj = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return True
    if user_obj.is_active:
        raise DRFValidationError(detail="Email was already verified. Proceed to login.")
    try:
        token_obj = EmailConfirmationToken.objects.filter(user=user_obj).first()
        if token_obj:
            token_obj.delete()
    except EmailConfirmationToken.DoesNotExist:
        send_verification_email(user=user_obj, email=email)
    send_verification_email(user=user_obj, email=email)
    return True
