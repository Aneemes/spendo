from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated

from .services import (
    create_expense_category, update_expense_category, delete_expense_category,
    create_income_category, update_income_category, delete_income_category
)
from .selectors import fetch_expense_categories, fetch_expense_category_detail, fetch_income_categories, fetch_income_category_detail

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


class CreateIncomeCategoryAPIview(APIView):
    permission_classes = [IsAuthenticated]

    class CreateIncomeCategoryInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        color_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class CreateIncomeCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.CreateIncomeCategoryInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            income_category_details = create_income_category(
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
        output_serializer = self.CreateIncomeCategoryOutputSerializer(income_category_details)
        return Response(
            {
                "success": True,
                "message": "Income category created successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    

class UpdateIncomeCategoryAPIview(APIView):
    """
    API endpoint to update an existing income category.
    This view allows authenticated users to update the details of a specific income category.
    The update can include the title, description, and color code of the category.
    Methods:
        patch: Updates an income category with the provided data.
    Input Serializer Fields:
        title (str): The new title for the income category.
        description (str, optional): A description of the income category.
        color_code (str, optional): A color code for visual representation.
    Output Serializer Fields:
        uid (UUID): The unique identifier of the income category.
        title (str): The updated title of the income category.
        description (str): The updated description of the income category.
        color_code (str): The updated color code of the income category.
    URL Parameters:
        category_uid (UUID): The unique identifier of the income category to update.
    Returns:
        Response: A JSON response containing:
            - success (bool): Indicates if the operation was successful.
            - message (str): A description of the operation result.
            - data (dict): The updated income category details.
    Raises:
        DjangoValidationError: If the input data fails model validation.
        DRFValidationError: If the input data fails serializer validation.
    Permission Classes:
        IsAuthenticated: Only authenticated users can access this endpoint.
    """
    permission_classes = [IsAuthenticated]

    class UpdateIncomeCategoryInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        color_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class UpdateIncomeCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        input_serializer = self.UpdateIncomeCategoryInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            income_category_details = update_income_category(
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
        output_serializer = self.UpdateIncomeCategoryOutputSerializer(income_category_details)
        return Response(
            {
                "success": True,
                "message": "Income category updated successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class ListIncomeCategoryAPIView(APIView):
    """
    A view for listing income categories.
    This API view allows authenticated users to retrieve a list of their income categories.
    Attributes:
        permission_classes (list): List containing IsAuthenticated permission class.
        ListIncomeCategoryOutputSerializer (class): Nested serializer class for output data format.
    Returns:
        Response: A JSON response containing:
            - success (bool): True if operation was successful, False otherwise
            - message (str): Description of the operation result
            - data (list): List of income categories with their details if successful
    Raises:
        DjangoValidationError: If there's an error in Django validation
        DRFValidationError: If there's an error in DRF validation
    Response Format:
            "success": bool,
            "message": str,
            "data": [
                    "uid": uuid,
                    "title": str,
                    "description": str,
                    "color_code": str,
                    "created_at": datetime,
                    "updated_at": datetime
                ...
            ]
        }
    """
    permission_classes = [IsAuthenticated]

    class ListIncomeCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
        updated_at = serializers.DateTimeField(read_only=True)

    def get(self, request, *args, **kwargs):
        try:
            income_categories = fetch_income_categories(user=request.user)
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
        output_serializer = self.ListIncomeCategoryOutputSerializer(income_categories, many=True)
        return Response(
            {
                "success": True,
                "message": "Income categories fetched successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )

class RetrieveIncomeCategoryAPIView(APIView):
    """
    API view for retrieving a specific income category.
    This view requires user authentication and provides detailed information about a single income category.
    Attributes:
        permission_classes (list): List containing IsAuthenticated permission class.
    Methods:
        get(request, *args, **kwargs): Retrieves the income category details.
    Output Serializer Fields:
        - uid (UUID): Unique identifier of the income category
        - title (str): Title of the income category
        - description (str): Description of the income category
        - color_code (str): Color code associated with the category
        - created_at (datetime): Timestamp of category creation
        - updated_at (datetime): Timestamp of last update
    Returns:
        Response: JSON response containing:
            - success (bool): Indicates if the request was successful
            - message (str): Description of the operation result
            - data (dict): Serialized income category data
    Raises:
        DjangoValidationError: If there's an error validating the category data
        DRFValidationError: If there's an error in the API validation
    """
    permission_classes = [IsAuthenticated]

    class RetrieveIncomeCategoryOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
        updated_at = serializers.DateTimeField(read_only=True)
    
    def get(self, request, *args, **kwargs):
        try:
            income_category = fetch_income_category_detail(
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
        output_serializer = self.RetrieveIncomeCategoryOutputSerializer(income_category)
        return Response(
            {
                "success": True,
                "message": "Income category fetched successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class DeleteIncomeCategoryAPIView(APIView):
    """
    API endpoint for deleting an income category.
    This view handles the deletion of income categories for authenticated users.
    It requires a category_uid parameter to identify the category to be deleted.
    Permissions:
        - User must be authenticated
    Args:
        request: The HTTP request object
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments, must contain 'category_uid'
    Returns:
        Response: A JSON response containing:
            - success (bool): Indicates if the operation was successful
            - message (str): A descriptive message about the operation result
    Raises:
        DjangoValidationError: If there's a validation error in the deletion process
        DRFValidationError: If there's a DRF-specific validation error
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            income_category = delete_income_category(
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
        return Response(
            {
                "success": True,
                "message": "Income category deleted successfully"
            },
            status=status.HTTP_200_OK
        )