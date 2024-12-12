import random
import string
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings

def check_if_email_is_taken(*, email: str) -> bool:

    try:
        existing_email = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return False
    return True

def send_reset_password_link(*, reset_link:str, receiver_email:str) -> bool:

    subject = "Password reset link."
    message = f"The password reset link is {reset_link}"
    email_from = settings.EMAIL_HOST
    email_to = receiver_email

    send_mail(subject, message, settings.EMAIL_HOST_USER, [email_to], fail_silently=False)

def generate_username_from_email(email):
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