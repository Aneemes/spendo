from django.urls import path

from .views import (
    CreateWalletAPIView,
    UpdateWalletAPIView,
    FetchWalletListAPIView,
    FetchWalletDetailAPIView,
    DeleteWalletAPIView
)

app_name = "wallet"

urlpatterns = [
    path('create/', CreateWalletAPIView.as_view(), name='create-income'),
    path('update/<uuid:wallet_uid>/', UpdateWalletAPIView.as_view(), name='update-income'),
    path('list/', FetchWalletListAPIView.as_view(), name='income-list'),
    path('detail/<uuid:wallet_uid>/', FetchWalletDetailAPIView.as_view(), name='detail-income'),
    path('delete/<uuid:wallet_uid>/', DeleteWalletAPIView.as_view(), name='income-delete')
]

