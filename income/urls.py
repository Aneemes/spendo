from django.urls import path

from .views import (
    CreateIncomeAPIView,
    UpdateIncomeAPIView,
    FetchIncomeListAPIView,
    FetchIncomeDetailAPIView,
    DeleteIncomeAPIView
)

app_name = "income"

urlpatterns = [
    path('create/', CreateIncomeAPIView.as_view(), name='create-income'),
    path('update/<uuid:income_uid>/', UpdateIncomeAPIView.as_view(), name='update-income'),
    path('list/', FetchIncomeListAPIView.as_view(), name='income-list'),
    path('detail/<uuid:income_uid>/', FetchIncomeDetailAPIView.as_view(), name='detail-income'),
    path('delete/<uuid:income_uid>/', DeleteIncomeAPIView.as_view(), name='income-delete')
]

