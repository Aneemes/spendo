from django.urls import path

from .views import (
    home,
    CreateExpenseCategoryAPIview,
    ListExpenseCategoryAPIView,
    UpdateExpenseCategoryAPIview,
    DeleteExpenseCategoryAPIView,
    RetrieveExpenseCategoryAPIView,
    CreateIncomeCategoryAPIview,
    ListIncomeCategoryAPIView,
    UpdateIncomeCategoryAPIview,
    DeleteIncomeCategoryAPIView,
    RetrieveIncomeCategoryAPIView
)

app_name = "core"

urlpatterns = [
    path("", home, name='home'),
    # for expense
    path("expense-category/create/", CreateExpenseCategoryAPIview.as_view(), name="create-expense-category"),
    path("expense-category/list/", ListExpenseCategoryAPIView.as_view(), name="list-expense-category"),
    path("expense-category/update/<uuid:category_uid>/", UpdateExpenseCategoryAPIview.as_view(), name="update-expense-category"),
    path("expense-category/delete/<uuid:category_uid>/", DeleteExpenseCategoryAPIView.as_view(), name="delete-expense-category"),
    path("expense-category/detail/<uuid:category_uid>/", RetrieveExpenseCategoryAPIView.as_view(), name="detail-expense-category"),

    # for income
    path("income-category/create/", CreateIncomeCategoryAPIview.as_view(), name="create-income-category"),
    path("income-category/list/", ListIncomeCategoryAPIView.as_view(), name="list-income-category"),
    path("income-category/update/<uuid:category_uid>/", UpdateIncomeCategoryAPIview.as_view(), name="update-income-category"),
    path("income-category/delete/<uuid:category_uid>/", DeleteIncomeCategoryAPIView.as_view(), name="delete-income-category"),
    path("income-category/detail/<uuid:category_uid>/", RetrieveIncomeCategoryAPIView.as_view(), name="detail-income-category"),
]

