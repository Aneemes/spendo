from django.shortcuts import render
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .services import create_income, update_income, delete_user_income
from .selectors import get_user_income_details, get_user_income_list

class CreateIncomeAPIView(APIView):
    """
    API view for creating income records.
    This view handles POST requests to create new income entries. It requires user authentication
    and validates the input data using CreateIncomeInputSerializer.
    Attributes:
        permission_classes (list): List containing IsAuthenticated to ensure only authenticated users can access
        CreateIncomeInputSerializer (Serializer): Inner serializer class that defines the expected input fields
    Methods:
        post(request, *args, **kwargs): Creates a new income record
    Input Fields:
        title (str, optional): Title of the income entry
        amount (decimal, required): Monetary value of the income with 2 decimal places
        date (date, required): Date of the income
        description (str, optional): Additional details about the income
        category_uid (UUID, optional): Unique identifier for the income category
    Returns:
        Response: JSON response with success status and message
            - 201: Income created successfully
            - 400: Validation error occurred
    Raises:
        DjangoValidationError: If income creation fails validation
        DRFValidationError: If request data validation fails
    """
    permission_classes = [IsAuthenticated]

    class CreateIncomeInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        date = serializers.DateField(required=False)
        description = serializers.CharField(required=False)
        category = serializers.UUIDField(required=False)
        wallet = serializers.UUIDField(required=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.CreateIncomeInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            income = create_income(
                **input_serializer.validated_data,
                user=request.user
            )
        except DjangoValidationError as e:
            return Response(
                {
                    'success': False,
                    'message': e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DRFValidationError as e:
            return Response(
                {
                    'success': False,
                    'message': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                'success': True,
                'message': 'New income created successfully.'
            },
            status=status.HTTP_201_CREATED
        )

class UpdateIncomeAPIView(APIView):
    """
    API view for updating an existing income record.
    This view requires user authentication and handles the update of income records
    with atomic transaction support.
    Attributes:
        permission_classes (list): List containing IsAuthenticated permission class.
    Methods:
        put(request, *args, **kwargs): Handles PUT requests to update income records.
    Input Fields:
        - title (str, optional): The title of the income record
        - amount (decimal, required): The monetary amount of income (max 10 digits, 2 decimal places)
        - date (date, required): The date of the income
        - description (str, optional): Additional details about the income
        - category_uid (UUID, optional): Unique identifier for the income category
    Returns:
        Response: A JSON response with:
            - success (bool): Indicates if the operation was successful
            - message (str): Description of the operation result
    Status Codes:
        - 200: Income successfully updated
        - 400: Invalid input data or validation error
        - 401: Authentication credentials not provided
    """
    permission_classes = [IsAuthenticated]

    class UpdateIncomeInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        date = serializers.DateField(required=True)
        description = serializers.CharField(required=False)
        category = serializers.UUIDField(required=False)
        wallet = serializers.UUIDField(required=True)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        input_serializer = self.UpdateIncomeInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            update_income(
                user = request.user,
                income_uid = kwargs.get('income_uid'),
                **input_serializer.validated_data,
            )
        except DjangoValidationError as e:
            return Response(
                {
                    'success': False,
                    'message': e.message
                }, status=status.HTTP_400_BAD_REQUEST
            )
        except DRFValidationError as e:
            return Response(
                {
                    'success': False,
                    'message': e.detail
                }, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                'success': True,
                'message': 'Income updated successfully.'
            }, status=status.HTTP_200_OK
        )

class FetchIncomeListAPIView(APIView):
    """
    A view for fetching a paginated list of income records.
    This API view requires authentication and provides various filtering options for retrieving income records.
    It uses pagination to limit the number of records returned per request.
    Attributes:
        permission_classes (list): List containing IsAuthenticated permission class.
        page_size (int): Number of records per page (default: 20).
        max_page_size (int): Maximum allowed page size (default: 100).
    Query Parameters:
        title (str, optional): Filter incomes by title.
        start_date (date, optional): Filter incomes from this date.
        end_date (date, optional): Filter incomes until this date.
        category_uid (UUID, optional): Filter incomes by category UUID.
        date_filter (str, optional): Predefined date filter option.
        page (int, optional): Page number for pagination.
        page_size (int, optional): Number of records per page (1-100).
    Returns:
        Response: A JSON response containing:
            - success (bool): Operation success status
            - message (str): Success/error message
            - count (int): Total number of records
            - next (str): URL for next page
            - previous (str): URL for previous page
            - data (list): List of income records with their details
    Raises:
        DjangoValidationError: If there's an error in Django validation
        DRFValidationError: If there's an error in DRF validation
    Examples:
        GET /api/income/list/
        GET /api/income/list/?title=Salary&start_date=2023-01-01
    """
    permission_classes = [IsAuthenticated]

    class FetchIncomeListOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        date = serializers.DateField(read_only=True)
        amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
        category = serializers.UUIDField(read_only=True)
        category_title = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
        updated_at = serializers.DateTimeField(read_only=True)

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            if instance.category:
                representation['category_title'] = instance.category.title
                representation['color_code'] = instance.category.color_code
            return representation
        
    class Pagination(PageNumberPagination):
        page_size = 20
        page_size_query_param = 'page_size'
        max_page_size = 100
    
    def get(self, request, *args, **kwargs):
        try:
            title = request.query_params.get('title', None)
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)
            category_uid = request.query_params.get('category', None)
            date_filter = request.query_params.get('date_filter', None)
            
            income_list = get_user_income_list(
                user=request.user,
                title=title,
                start_date=start_date,
                end_date=end_date,
                category_uid=category_uid,
                date_filter=date_filter
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
        paginator = self.Pagination()
        paginated_incomes = paginator.paginate_queryset(income_list, request)
        output_serializer = self.FetchIncomeListOutputSerializer(paginated_incomes, many=True)

        response_data = {
            "success": True,
            "message": "Income list fetched successfully",
            "count": income_list.count(),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "data": output_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class FetchIncomeDetailAPIView(APIView):
    """
    API endpoint to fetch detailed information about a specific income record.
    This view requires authentication and handles the retrieval of income details
    for a specific income record identified by its UUID.
    Attributes:
        permission_classes (list): List containing IsAuthenticated permission class
        RetrieveIncomeDetailOutputSerializer (Serializer): Inner serializer class for formatting output data
    Methods:
        get(request, *args, **kwargs): Handles GET requests to fetch income details
    Returns:
        Response: A JSON response containing:
            - success (bool): Indicates if the operation was successful
            - message (str): Description of the operation result
            - data (dict): Serialized income details including:
                - uid (UUID): Unique identifier of the income
                - title (str): Title of the income
                - description (str): Description of the income
                - date (date): Date of the income
                - amount (decimal): Amount of the income
                - category (UUID): Category identifier
                - category_title (str): Title of the category
                - color_code (str): Color code for the category
                - created_at (datetime): Creation timestamp
                - updated_at (datetime): Last update timestamp
    Raises:
        DjangoValidationError: If there's an error in Django validation
        DRFValidationError: If there's an error in DRF validation
    Status Codes:
        200: Successfully retrieved income details
        400: Bad request due to validation errors
    """
    permission_classes = [IsAuthenticated]

    class RetrieveIncomeDetailOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        date = serializers.DateField(read_only=True)
        amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
        category = serializers.UUIDField(read_only=True)
        category_title = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
        updated_at = serializers.DateTimeField(read_only=True)

    def get(self, request, *args, **kwargs):
        try:
            income_details = get_user_income_details(
                user=request.user,
                income_uid=kwargs.get("income_uid")
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
        output_serializer = self.RetrieveIncomeDetailOutputSerializer(income_details)
        return Response(
            {
                "success": True,
                "message": "Income fetched successfully.",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class DeleteIncomeAPIView(APIView):
    """
    API view for deleting a user's income record.
    This view requires user authentication and handles the deletion of income records
    through an atomic transaction.
    Attributes:
        permission_classes (list): List containing IsAuthenticated permission class to ensure
            only authenticated users can access this view.
    Methods:
        delete(request, *args, **kwargs): Handles DELETE requests to remove income records.
    Returns:
        Response: A JSON response with:
            - success (bool): Indicates if operation was successful
            - message (str): Description of the operation result
            Status codes:
                - 200: Successful deletion
                - 400: Invalid request or validation error
    Raises:
        DjangoValidationError: When validation fails at the Django model level
        DRFValidationError: When validation fails at the DRF level
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            income_deletion_status = delete_user_income(
                user=request.user,
                income_uid=kwargs.get("income_uid")
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
                "message": "Income deleted successfully."
            },
            status=status.HTTP_200_OK
        )