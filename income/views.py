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
    permission_classes = [IsAuthenticated]

    class CreateIncomeInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        date = serializers.DateField(required=True)
        description = serializers.CharField(required=False)
        category_uid = serializers.UUIDField(required=False)

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
                    'message': e.message
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
    permission_classes = [IsAuthenticated]

    class UpdateIncomeInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        date = serializers.DateField(required=True)
        description = serializers.CharField(required=False)
        category_uid = serializers.UUIDField(required=False)

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