from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError

from account.models import CustomUser

from .models import Wallet
from .selectors import get_wallet_from_uid_and_user

def create_wallet(
    *, 
    title:str, 
    balance:Decimal,
    color:str = "#007bff",
    user:CustomUser
) -> bool:
    
    wallet_instance = Wallet(
        title = title.strip(),
        balance = balance,
        color = color,
        user = user
    )

    try:
        wallet_instance.full_clean()
        wallet_instance.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(detail=e.messages[0])

    return True 


@transaction.atomic
def update_wallet(
    *,
    title:str,
    balance:str,
    color:str = "#007bff",
    wallet_uid:UUID,
    user:CustomUser
) -> bool:
    wallet_instance = get_wallet_from_uid_and_user(wallet_uid=wallet_uid,user=user)
    if wallet_instance is None:
        raise DRFValidationError(detail="wallet not found.")
    
    wallet_instance.title = title
    wallet_instance.balance = balance
    wallet_instance.color = color

    try:
        wallet_instance.full_clean()
        wallet_instance.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    
    return True
    
@transaction.atomic
def delete_wallet(
    *,
    wallet_uid:UUID,
    user:CustomUser
) -> bool:
    wallet_instance = get_wallet_from_uid_and_user(wallet_uid=wallet_uid,user=user)
    if wallet_instance is None:
        raise DRFValidationError(detail="wallet not found.")
    
    wallet_instance.delete()
    return True