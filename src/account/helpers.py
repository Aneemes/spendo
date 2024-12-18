import random
import string
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings

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

def send_reset_password_link(*, reset_link:str, receiver_email:str) -> bool:
    """
    Sends a password reset link to the specified email address.
    Args:
        reset_link (str): The URL for resetting the password.
        receiver_email (str): The email address of the recipient.
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """

    subject = "Password reset link."
    message = f"The password reset link is {reset_link}"
    email_from = settings.EMAIL_HOST
    email_to = receiver_email

    send_mail(subject, message, settings.EMAIL_HOST_USER, [email_to], fail_silently=False)

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

# {
#     "full_name": "Animesh Nepal",
#     "email": "aneemes1@gmail.com",
#     "password": "strongpass123",
#     "confirm_password": "strongpass123"
# }

# {
#     "email": "aneemes1@gmail.com",
#     "password": "strongpass123"
# }