from django.shortcuts import render
from django.utils.timezone import now
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError

from .selectors import get_transaction_list

class FetchTransactionViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class FetchTransactionOutputSerializer(serializers.Serializer):
        date = serializers.DateField()
        amount = serializers.DecimalField(max_digits=12, decimal_places=2)
        transactions = serializers.ListField(child=serializers.DictField())

    def get(self, request, *args, **kwargs):
        try:
            # Get parameters from query string instead of URL path
            transaction_data = get_transaction_list(
                user=request.user,
                transaction_type=kwargs.get('transaction_type', request.query_params.get('transaction_type', 'all')),
                year=request.query_params.get('year', str(now().year)),
                month=request.query_params.get('month', str(now().month))
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
            
        serializer = self.FetchTransactionOutputSerializer(transaction_data, many=True)
        return Response(
            {
                "success": True,
                "message": "Transactions list fetched successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )