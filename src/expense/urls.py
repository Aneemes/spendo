from django.urls import path

from .views import *

app_name = "expense"

urlpatterns = [
    path("create/", CreateExpenseAPIView.as_view(), name="create-expense"),
    path("update/<uuid:expense_uid>/", UpdateExpenseAPIView.as_view(), name="update-expense"),
    path("list/", FetchExpenseListAPIView.as_view(), name="list-expense"),
    path("detail/<uuid:expense_uid>/", FetchExpenseDetailAPIView.as_view(), name="detail-expense"),
    path("delete/<uuid:expense_uid>/", DeleteExpenseAPIView.as_view(), name="delete-expense"),
]

