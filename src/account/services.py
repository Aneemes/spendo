from django.db import transaction
from .models import CustomUser
from dataclasses import dataclass
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError as DjangoValidationError
from .helpers import check_if_email_is_taken, send_reset_password_link, generate_username_from_email

@transaction.atomic
def user_signup(
    *,
    full_name: str,
    email: str,
    password: str,
    confirm_password: str
) -> str:
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
    @dataclass(frozen=True)
    class UserSignupDetails:
        full_name: str
        username: str
        access_token: str
    
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
    )

    try:
        user.set_password(password)
        user.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    user.save()

    token = RefreshToken.for_user(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    signup_details = UserSignupDetails(
        full_name, username, access_token
    )


    return signup_details, refresh_token

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
        access_token: str
    
    user = CustomUser.objects.get(email=email.lower())
    if user is None:
        raise DjangoValidationError("Invalid credentials.")
    
    if not user.check_password(password):
        raise DjangoValidationError("Invalid credentials.")
    
    full_name = user.full_name
    username = user.username


    token = RefreshToken.for_user(user)
    access_token = str(token.access_token)
    refresh_token = str(token)

    login_details = UserLoginDetails(
        full_name, username, access_token
    )

    return login_details, refresh_token

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
    
    user = CustomUser.objects.get(email=email)
    if user is None:
        raise DjangoValidationError("Please enter a valid email address.")
    token = get_random_string(length=64)
    user.password = token
    user.save()

    username = user.username

    reset_link = f"http://127.0.0.1:8000/auth/reset-password/{username}/{token}"
    email = send_reset_password_link(reset_link=reset_link, receiver_email=email)
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
    
    user = CustomUser.objects.get(username=username)
    if not user:
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
    
