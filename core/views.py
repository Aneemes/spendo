from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated

from .services import create_expense_category, update_expense_category, delete_expense_category
from .selectors import fetch_expense_categories, fetch_expense_category_detail

class CreateExpenseCategoryAPIview(APIView):
    """
    API view to create an expense category.
    This view handles the creation of a new expense category for an authenticated user.
    It validates the input data, creates the expense category, and returns the details of the created category.
    Attributes:
        permission_classes (list): List of permission classes that are required to access this view.
    Inner Classes:
        CreateExpenseCategoryInputSerializer (serializers.Serializer): Serializer for input data.
            - title (serializers.CharField): Title of the expense category (optional).
            - description (serializers.CharField): Description of the expense category (optional).
            - color_code (serializers.CharField): Color code of the expense category (optional).
        CreateExpenseCategoryOutputSerializer (serializers.Serializer): Serializer for output data.
            - uid (serializers.UUIDField): Unique identifier of the created expense category.
            - title (serializers.CharField): Title of the created expense category.
            - description (serializers.CharField): Description of the created expense category.
            - color_code (serializers.CharField): Color code of the created expense category.
    Methods:
        post(request, *args, **kwargs):
            Handles the POST request to create a new expense category.
            Validates the input data, creates the expense category, and returns the details of the created category.
            Returns a success message and the created category details on success.
            Returns an error message on validation failure.
    """
    permission_classes = [IsAuthenticated]

    class CreateExpenseCategoryInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        color_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class CreateExpenseCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.CreateExpenseCategoryInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            category_details = create_expense_category(
                **input_serializer.validated_data,
                user=request.user
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        output_serializer = self.CreateExpenseCategoryOutputSerializer(category_details)
        return Response(
            {
                "success": True,
                "message": "Expense category created successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class UpdateExpenseCategoryAPIview(APIView):
    """
    API view to handle updating an expense category.
    This view allows authenticated users to update the details of an existing expense category.
    The input data is validated using the `UpdateExpenseCategoryInputSerializer` and the response
    data is serialized using the `UpdateExpenseCategoryOutputSerializer`.
    Attributes:
        permission_classes (list): List of permission classes that are required to access this view.
    Inner Classes:
        UpdateExpenseCategoryInputSerializer (serializers.Serializer): Serializer for validating input data.
        UpdateExpenseCategoryOutputSerializer (serializers.Serializer): Serializer for formatting output data.
    Methods:
        patch(request, *args, **kwargs):
            Handles the PATCH request to update an expense category.
            Validates the input data, updates the category, and returns the updated category details.
            Returns a 400 status code with an error message if validation fails.
            Returns a 201 status code with the updated category details if the update is successful.
    """
    permission_classes = [IsAuthenticated]

    class UpdateExpenseCategoryInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        color_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class UpdateExpenseCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        input_serializer = self.UpdateExpenseCategoryInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            category_details = update_expense_category(
                **input_serializer.validated_data,
                category_uid=kwargs.get("category_uid"),
                user=request.user
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        output_serializer = self.UpdateExpenseCategoryOutputSerializer(category_details)
        return Response(
            {
                "success": True,
                "message": "Expense category updated successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class ListExpenseCategoryAPIView(APIView):
    """
    API view to list expense categories for an authenticated user.
    This view handles GET requests to fetch a list of expense categories associated with the authenticated user.
    It uses the `ListExpenseCategoryOutputSerializer` to serialize the output data.
    Attributes:
        permission_classes (list): List of permission classes that this view requires. In this case, it requires the user to be authenticated.
    Inner Classes:
        ListExpenseCategoryOutputSerializer (serializers.Serializer): Serializer class for the output data. It includes the following fields:
            - uid (UUIDField): Unique identifier of the expense category.
            - title (CharField): Title of the expense category.
            - description (CharField): Description of the expense category.
            - color_code (CharField): Color code associated with the expense category.
            - created_at (DateTimeField): Timestamp when the expense category was created.
            - updated_at (DateTimeField): Timestamp when the expense category was last updated.
    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to fetch expense categories.
            Returns a JSON response with the list of expense categories or an error message if validation fails.
    """
    permission_classes = [IsAuthenticated]

    class ListExpenseCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
        updated_at = serializers.DateTimeField(read_only=True)

    def get(self, request, *args, **kwargs):
        try:
            expense_categories = fetch_expense_categories(user=request.user)
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        output_serializer = self.ListExpenseCategoryOutputSerializer(expense_categories, many=True)
        return Response(
            {
                "success": True,
                "message": "Expense categories fetched successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )

class RetrieveExpenseCategoryAPIView(APIView):
    """
    RetrieveExpenseCategoryAPIView is a Django Rest Framework API view that handles
    the retrieval of an expense category for an authenticated user.
    Attributes:
        permission_classes (list): A list of permission classes that the user must
            satisfy to access this view. In this case, the user must be authenticated.
    Inner Classes:
        RetrieveExpenseCategoryOutputSerializer (serializers.Serializer): A serializer
            class used to format the output data of the expense category. It includes
            the following fields:
                - uid (UUIDField): The unique identifier of the expense category.
                - title (CharField): The title of the expense category.
                - description (CharField): The description of the expense category.
                - color_code (CharField): The color code associated with the expense category.
                - created_at (DateTimeField): The timestamp when the expense category was created.
                - updated_at (DateTimeField): The timestamp when the expense category was last updated.
    Methods:
        get(self, request, *args, **kwargs):
            Handles GET requests to retrieve the details of an expense category.
            Args:
                request (Request): The HTTP request object.
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments, including 'category_uid' which
                    is the unique identifier of the expense category to be retrieved.
            Returns:
                Response: A DRF Response object containing the serialized expense category
                    data if successful, or an error message if validation fails.
    """
    permission_classes = [IsAuthenticated]

    class RetrieveExpenseCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
        updated_at = serializers.DateTimeField(read_only=True)
    
    def get(self, request, *args, **kwargs):
        try:
            expense_category = fetch_expense_category_detail(
                user=request.user,
                category_uid=kwargs.get("category_uid")
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        output_serializer = self.RetrieveExpenseCategoryOutputSerializer(expense_category)
        return Response(
            {
                "success": True,
                "message": "Expense category fetched successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class DeleteExpenseCategoryAPIView(APIView):
    """
    APIView for deleting an expense category.
    This view handles the deletion of an expense category for an authenticated user.
    It requires the user to be authenticated and expects a category UID to be provided
    in the URL parameters.
    Methods:
        delete(request, *args, **kwargs): Deletes the specified expense category.
    Raises:
        DjangoValidationError: If there is a validation error from Django.
        DRFValidationError: If there is a validation error from Django REST Framework.
    Returns:
        Response: A DRF Response object with a success message and HTTP status code 200
                  if the deletion is successful, or an error message and HTTP status code
                  400 if there is a validation error.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            expense_category = delete_expense_category(
                user=request.user,
                category_uid=kwargs.get("category_uid")
            )
            expense_category.delete()
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": "Expense category deleted successfully"
            },
            status=status.HTTP_200_OK
        )