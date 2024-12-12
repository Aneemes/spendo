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
    
