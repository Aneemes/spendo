from django.urls import path

from .views import (
    FetchTransactionViewAPIView
)

app_name = "transaction"

urlpatterns = [
    path("list/", FetchTransactionViewAPIView.as_view(), name="list"),
]

