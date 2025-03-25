from django.urls import path

from .views import (
    CreateWalletAPIView,
    UpdateWalletAPIView,
    FetchWalletListAPIView,
    FetchWalletDetailAPIView,
    DeleteWalletAPIView,
    CreateTransferAPIView,
    FetchTransferListAPIView,
    FetchTransferDetailAPIView,
    UpdateTransferAPIView,
    DeleteTransferAPIView
)

app_name = "wallet"

urlpatterns = [
    path('create/', CreateWalletAPIView.as_view(), name='create-income'),
    path('update/<uuid:wallet_uid>/', UpdateWalletAPIView.as_view(), name='update-income'),
    path('list/', FetchWalletListAPIView.as_view(), name='income-list'),
    path('detail/<uuid:wallet_uid>/', FetchWalletDetailAPIView.as_view(), name='detail-income'),
    path('delete/<uuid:wallet_uid>/', DeleteWalletAPIView.as_view(), name='income-delete'),


    # Transfer endpoints
    path('transfer/create/', CreateTransferAPIView.as_view(), name='create-transfer'),
    path('transfer/list/', FetchTransferListAPIView.as_view(), name='transfer-list'),
    path('transfer/<uuid:transfer_uid>/', FetchTransferDetailAPIView.as_view(), name='transfer-detail'),
    path('transfer/update/<uuid:transfer_uid>/', UpdateTransferAPIView.as_view(), name='update-transfer'),
    path('transfer/delete/<uuid:transfer_uid>/', DeleteTransferAPIView.as_view(), name='delete-transfer'),
]

