from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from .services import (
    create_user_expense, update_user_expense, delete_user_expense
)
from .selectors import get_user_expense_details, get_user_expense_list

class CreateExpenseAPIView(APIView):
    """
    API view to handle the creation of a new expense.
    Attributes:
        permission_classes (list): List of permission classes that this view requires.
    Inner Class:
        CreateExpenseAPIView (serializers.Serializer): Serializer class to validate the input data for creating an expense.
            - title (serializers.CharField): Title of the expense, required but can be blank or null.
            - description (serializers.CharField): Description of the expense, optional and can be blank or null.
            - amount (serializers.DecimalField): Amount of the expense, required with a maximum of 10 digits and 2 decimal places.
            - category (serializers.UUIDField): UUID of the category to which the expense belongs, required.
    Methods:
        post(request, *args, **kwargs):
            Handles the POST request to create a new expense.
            Validates the input data using the inner serializer class.
            Creates the expense for the authenticated user.
            Returns a success response if the expense is created successfully.
            Returns an error response if there is a validation error.
    """
    permission_classes = [IsAuthenticated]

    class CreateExpenseAPIView(serializers.Serializer):
        title = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        category = serializers.UUIDField(required=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.CreateExpenseAPIView(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            expense_creation_status = create_user_expense(
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
        return Response(
            {
                "success": True,
                "message": "Expense created successfully"
            },
            status=status.HTTP_201_CREATED
        )
        
class UpdateExpenseAPIView(APIView):
    """
    API view to handle updating an expense.
    Methods
    -------
    patch(request, *args, **kwargs)
        Handles the PATCH request to update an expense.
    Inner Classes
    -------------
    UpdateExpenseInputSerializer(serializers.Serializer)
        Serializer to validate the input data for updating an expense.
    Attributes
    ----------
    permission_classes : list
        List of permission classes that are required to access this view.
    ---------
    Serializer to validate the input data for updating an expense.
        Fields
        ------
        title : serializers.CharField
            The title of the expense (optional).
        description : serializers.CharField
            The description of the expense (optional).
        amount : serializers.DecimalField
            The amount of the expense (optional).
        category : serializers.UUIDField
            The category of the expense (optional).
        Methods
        -------
        validate_category(value)
            Validates the category field, allowing empty strings to be treated as None.
    """
    permission_classes = [IsAuthenticated]

    class UpdateExpenseInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        amount = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
        category = serializers.UUIDField(required=False, allow_null=True)

        def validate_category(self, value):
            if value == "":
                return None
            return value

    @extend_schema(
        request=UpdateExpenseInputSerializer,
        responses={
            200: OpenApiResponse(description="Expense updated successfully"),
            400: OpenApiResponse(description="Bad request, invalid input")
        }
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        input_serializer = self.UpdateExpenseInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            update_expense_status = update_user_expense(
                **input_serializer.validated_data,
                user=request.user,
                expense_uid=kwargs.get("expense_uid")
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
                "message": "Expense updated successfully"
            },
            status=status.HTTP_200_OK
        )
    
class FetchExpenseListAPIView(APIView):
    """
    API view to fetch a list of expenses for an authenticated user.
    Attributes:
        permission_classes (list): List of permission classes that this view requires.
        FetchExpenseListOutputSerializer (class): Serializer class for output representation of expense list.
        Pagination (class): Pagination class for paginating the expense list.
    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to fetch the expense list based on query parameters.
            Query Parameters:
                - title (str, optional): Filter expenses by title.
                - start_date (str, optional): Filter expenses by start date.
                - end_date (str, optional): Filter expenses by end date.
                - category (str, optional): Filter expenses by category UUID.
                - date_filter (str, optional): Filter expenses by date filter.
            Returns:
                Response: A paginated list of expenses with success status and message.
    """
    permission_classes = [IsAuthenticated]

    class FetchExpenseListOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
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
            
            expense_list = get_user_expense_list(
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
        paginated_expenses = paginator.paginate_queryset(expense_list, request)
        output_serializer = self.FetchExpenseListOutputSerializer(paginated_expenses, many=True)

        response_data = {
            "success": True,
            "message": "Expense list fetched successfully",
            "count": expense_list.count(),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "data": output_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class FetchExpenseDetailAPIView(APIView):
    """
    API view to fetch the details of a specific expense for an authenticated user.
    Permission Classes:
        - IsAuthenticated: Ensures that the user is authenticated.
    Inner Class:
        RetrieveExpenseOutputSerializer: Serializer to format the output data of the expense details.
    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to retrieve expense details.
            Parameters:
                - request: The HTTP request object.
                - *args: Additional positional arguments.
                - **kwargs: Additional keyword arguments, expects 'expense_uid' to identify the expense.
            Returns:
                - Response: A DRF Response object containing the success status, message, and serialized expense data.
            Exceptions:
                - DjangoValidationError: Returns a 400 response with the validation error message.
                - DRFValidationError: Returns a 400 response with the validation error details.
    """
    permission_classes = [IsAuthenticated]

    class RetrieveExpenseOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
        category = serializers.UUIDField(read_only=True)
        category_title = serializers.CharField(read_only=True)
        color_code = serializers.CharField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
        updated_at = serializers.DateTimeField(read_only=True)

    def get(self, request, *args, **kwargs):
        try:
            expense_details = get_user_expense_details(
                user=request.user,
                expense_uid=kwargs.get("expense_uid")
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
        output_serializer = self.RetrieveExpenseOutputSerializer(expense_details)
        return Response(
            {
                "success": True,
                "message": "Expense fetched successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class DeleteExpenseAPIView(APIView):
    """
    DeleteExpenseAPIView is an API view that handles the deletion of a user's expense.
    Attributes:
        permission_classes (list): A list containing the permission classes that are required to access this view.
    Methods:
        delete(request, *args, **kwargs):
            Handles the HTTP DELETE request to delete a user's expense.
            Args:
                request (Request): The HTTP request object.
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments, including 'expense_uid' which is the unique identifier of the expense to be deleted.
            Returns:
                Response: A DRF Response object indicating the success or failure of the deletion operation.
            Raises:
                DjangoValidationError: If there is a validation error from Django.
                DRFValidationError: If there is a validation error from Django REST Framework.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            expense_deletion_status = delete_user_expense(
                user=request.user,
                expense_uid=kwargs.get("expense_uid")
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
                "message": "Expense deleted successfully"
            },
            status=status.HTTP_200_OK
        )