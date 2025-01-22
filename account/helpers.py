import random
import string

from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import CustomUser, EmailConfirmationToken

def check_if_email_is_taken(*, email: str) -> bool:
    """
    Check if the given email is already taken by an existing user.
    Args:
        email (str): The email address to check.
    Returns:
        bool: True if the email is already taken, False otherwise.
    """
    try:
        existing_email = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return False
    return True

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_reset_password_link(*, reset_link: str, receiver_email: str, user: CustomUser) -> bool:
    """
    Sends a password reset link to the specified email address.
    
    Args:
        reset_link (str): The URL for resetting the password.
        receiver_email (str): The email address of the recipient.
        user_name (str, optional): The name of the user (for personalization).
        
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """

    subject = "Reset Your Password"
    context = {
        "reset_link": reset_link,
        "user_name": user.username or "User",  # Default to "User" if no name is provided
    }

    # Render email content
    html_message = render_to_string("emails/password_reset.html", context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER

    try:
        # Send the email
        send_mail(
            subject,
            plain_message,
            from_email,
            [receiver_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log or handle the error
        print(f"Error sending reset password email: {e}")
        return False


def generate_username_from_email(email):
    """
    Generates a unique username based on the provided email address.
    The function extracts the base username from the email (the part before the '@' symbol)
    and checks if it is already taken in the database. If the base username is taken, it appends
    a random 4-character suffix (consisting of lowercase letters and digits) to the base username
    and checks again. This process repeats until a unique username is found.
    Args:
        email (str): The email address to generate the username from.
    Returns:
        str: A unique username derived from the email address.
    """
    base_username = email.split('@')[0]
    
    def is_username_taken(username):
        return CustomUser.objects.filter(username=username).exists()
    
    username = base_username
    while is_username_taken(username):
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        username = f"{base_username}_{random_suffix}"

    return username

def send_email_confirmation(user: CustomUser, email: str, token: str):
    """
    Sends the actual email for verification.
    """
    # Construct the confirmation URL
    confirmation_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = "Confirm Your Email Address"
    context = {
        "user": user,
        "confirmation_url": confirmation_url,
    }

    # Render email content
    html_message = render_to_string("emails/email_confirmation.html", context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER

    try:
        # Use Django's send_mail to send the email
        send_mail(
            subject,
            plain_message,
            from_email,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log or handle errors in email sending
        print(f"Error sending verification email: {e}")
        return False

def send_verification_email(user:CustomUser, email:str):
    """
    Handles email confirmation logic: generating a token, saving to the database, 
    and sending the email.
    """
    # Generate a random token
    generated_token = get_random_string(length=64)

    # Create the email confirmation token instance
    email_confirmation = EmailConfirmationToken(
        user=user,
        email=email.lower(),
        token=generated_token
    )

    try:
        email_confirmation.full_clean()
        email_confirmation.save()
    except DjangoValidationError:
        # Avoid breaking signup due to validation issues
        return False

    # Call helper function to send email
    if not send_email_confirmation(user=user, email=email, token=generated_token):
        return False

    return True


