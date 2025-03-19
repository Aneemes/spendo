from uuid import UUID

from account.models import CustomUser

from .models import Wallet

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