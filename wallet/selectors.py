from uuid import UUID

from account.models import CustomUser

from .models import Wallet, TransferTransaction

def get_wallet_from_uid_and_user(wallet_uid:UUID,user:CustomUser) -> Wallet:
    try:
        wallet_instance = Wallet.objects.get(uid=wallet_uid, user=user)
    except Wallet.DoesNotExist:
        return None
    return wallet_instance

def fetch_wallet_list(user:CustomUser) -> list[Wallet]:
    try:
        wallets = user.wallet.all()
    except Wallet.DoesNotExist:
        return []
    return wallets

def fetch_wallet_detail(wallet_uid:UUID,user:CustomUser) -> Wallet:
    try:
        wallet_instance = Wallet.objects.get(uid=wallet_uid, user=user)
    except Wallet.DoesNotExist:
        return None
    return wallet_instance

def get_wallet_from_uid_and_user(wallet_uid:UUID,user:CustomUser) -> Wallet:
    try:
        wallet_instance = Wallet.objects.get(uid=wallet_uid, user=user)
    except Wallet.DoesNotExist:
        return None
    return wallet_instance


def get_transfer_list(*, user: CustomUser):
    """
    Get all transfers for a user.
    
    Args:
        user (CustomUser): The user whose transfers to retrieve.
        
    Returns:
        QuerySet: QuerySet of TransferTransaction objects.
    """
    try:
        transfers = TransferTransaction.objects.filter(user=user)
    except TransferTransaction.DoesNotExist:
        return []
    return transfers
    
def get_transfer_detail(*, transfer_uid: UUID, user: CustomUser) -> TransferTransaction:
    """
    Get details of a specific transfer.
    
    Args:
        transfer_uid (UUID): UID of the transfer.
        user (CustomUser): User who owns the transfer.
        
    Returns:
        TransferTransaction: The transfer transaction.
        
    Raises:
        DRFValidationError: If transfer not found.
    """
    try:
        transfer = TransferTransaction.objects.get(uid=transfer_uid, user=user)
    except TransferTransaction.DoesNotExist:
        return None
    return transfer