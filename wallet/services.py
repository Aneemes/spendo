from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError

from account.models import CustomUser

from .models import Wallet, TransferTransaction
from .selectors import get_wallet_from_uid_and_user, get_transfer_detail

def create_wallet(
    *, 
    title:str, 
    balance:Decimal,
    color:str = "#007bff",
    user:CustomUser
) -> Wallet:
    
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

    return wallet_instance 


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

@transaction.atomic
def create_transfer(
    *,
    source_wallet_uid: UUID,
    destination_wallet_uid: UUID, 
    amount: Decimal,
    description: str = None,
    user: CustomUser
) -> TransferTransaction:
    """
    Transfer amount from one wallet to another.
    
    Args:
        source_wallet_uid (UUID): UID of the source wallet.
        destination_wallet_uid (UUID): UID of the destination wallet.
        amount (Decimal): Amount to transfer.
        description (str, optional): Description of the transfer. Defaults to None.
        user (CustomUser): User performing the transfer.
        
    Returns:
        TransferTransaction: The created transfer transaction.
        
    Raises:
        DRFValidationError: If source or destination wallet not found.
    """
    # Validate the amount
    if amount <= 0:
        raise DRFValidationError(detail="Transfer amount must be greater than zero.")
        
    # Get source and destination wallets
    source_wallet = get_wallet_from_uid_and_user(wallet_uid=source_wallet_uid, user=user)
    if not source_wallet:
        raise DRFValidationError(detail="Source wallet not found.")
        
    destination_wallet = get_wallet_from_uid_and_user(wallet_uid=destination_wallet_uid, user=user)
    if not destination_wallet:
        raise DRFValidationError(detail="Destination wallet not found.")
    
    if source_wallet == destination_wallet:
        raise DRFValidationError(detail="Source and destination wallets cannot be the same.")
    
    # Perform the transfer
    source_wallet.transfer_balance(destination_wallet, amount)
    
    # Create transfer record
    transfer = TransferTransaction(
        source_wallet=source_wallet,
        destination_wallet=destination_wallet,
        amount=amount,
        description=description.strip() if description and description.strip() else None,
        user=user,
    )
    
    try:
        transfer.full_clean()
        transfer.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(message=e.messages)
        
    return transfer

@transaction.atomic
def update_transfer(
    *,
    transfer_uid: UUID,
    amount: Decimal = None,
    description: str = None,
    user: CustomUser
) -> TransferTransaction:
    """
    Update an existing transfer.
    
    Args:
        transfer_uid (UUID): UID of the transfer to update.
        amount (Decimal, optional): New amount for the transfer.
        description (str, optional): New description for the transfer.
        user (CustomUser): User who owns the transfer.
        
    Returns:
        TransferTransaction: The updated transfer transaction.
        
    Raises:
        DRFValidationError: If transfer not found or amount is invalid.
    """
    transfer = get_transfer_detail(transfer_uid=transfer_uid, user=user)
    
    if amount is not None:
        if amount <= 0:
            raise DRFValidationError(detail="Transfer amount must be greater than zero.")
        
        # Reverse previous transfer
        if transfer.destination_wallet and transfer.source_wallet:
            transfer.destination_wallet.transfer_balance(transfer.source_wallet, transfer.amount)
        
        # Perform new transfer
        if transfer.source_wallet and transfer.destination_wallet:
            transfer.source_wallet.transfer_balance(transfer.destination_wallet, amount)
        
        transfer.amount = amount
        
    if description is not None:
        transfer.description = description.strip() if description and description.strip() else None
    
    try:
        transfer.full_clean()
        transfer.save()
    except DjangoValidationError as e:
        raise DjangoValidationError(message=e.messages)
        
    return transfer

@transaction.atomic
def delete_transfer(*, transfer_uid: UUID, user: CustomUser) -> bool:
    """
    Delete a transfer and reverse its effects on wallets.
    
    Args:
        transfer_uid (UUID): UID of the transfer to delete.
        user (CustomUser): User who owns the transfer.
        
    Returns:
        bool: True if deletion was successful.
        
    Raises:
        DRFValidationError: If transfer not found.
    """
    transfer = get_transfer_detail(transfer_uid=transfer_uid, user=user)
    if not transfer:
        raise DRFValidationError(detail="Transfer not found.")
    
    # Reverse the transfer
    if transfer.source_wallet and transfer.destination_wallet:
        transfer.destination_wallet.transfer_balance(transfer.source_wallet, transfer.amount)
    
    transfer.delete()
    return True