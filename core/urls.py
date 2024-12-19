from django.urls import path

from .views import *

app_name = "core"

urlpatterns = [
    path("expense-category/create/", CreateExpenseCategoryAPIview.as_view(), name="create-expense-category"),
    path("expense-category/list/", ListExpenseCategoryAPIView.as_view(), name="list-expense-category"),
    path("expense-category/update/<uuid:category_uid>/", UpdateExpenseCategoryAPIview.as_view(), name="update-expense-category"),
    path("expense-category/delete/<uuid:category_uid>/", DeleteExpenseCategoryAPIView.as_view(), name="delete-expense-category"),
    path("expense-category/detail/<uuid:category_uid>/", RetrieveExpenseCategoryAPIView.as_view(), name="detail-expense-category"),
]

