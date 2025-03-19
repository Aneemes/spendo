from django.shortcuts import render
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .services import create_wallet, update_wallet, delete_wallet
from .selectors import fetch_wallet_list, fetch_wallet_detail

class CreateWalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class CreateWalletInputSerializer(serializers.Serializer):
        title = serializers.CharField(write_only=True, required=True)
        balance = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        color = serializers.CharField(required=False)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.CreateWalletInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            wallet_creation_status = create_wallet(
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
                'message': 'New wallet created successfully.'
            },
            status=status.HTTP_201_CREATED
        )
    
class UpdateWalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class UpdateWalletInputSerializer(serializers.Serializer):
        title = serializers.CharField(write_only=True, required=True)
        balance = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        color = serializers.CharField(write_only=True, required=False)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.UpdateWalletInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            wallet_update_status = update_wallet(
                **input_serializer.validated_data,
                wallet_uid = kwargs.get('wallet_uid'),
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
                'message': 'Wallet updated successfully.'
            },
            status=status.HTTP_201_CREATED
        )

class FetchWalletListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class FetchWalletListOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.UUIDField(read_only=True)
        balance = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        color = serializers.CharField(read_only=True)

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        try:
            wallet_list = fetch_wallet_list(
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
        output_serializer = self.FetchWalletListOutputSerializer(wallet_list, many=True)
        return Response(
            {
                'success': True,
                'message': 'Wallet updated successfully.',
                'data': output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class FetchWalletDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class FetchWalletDetailOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField(read_only=True)
        title = serializers.UUIDField(read_only=True)
        balance = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        color = serializers.CharField(read_only=True)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            wallet = fetch_wallet_detail(
                wallet_uid = kwargs.get('wallet_uid'),
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
        output_serializer = self.FetchWalletDetailOutputSerializer(wallet)
        return Response(
            {
                'success': True,
                'message': 'Wallet updated successfully.',
                'data': output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class DeleteWalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            wallet_deletion_status = delete_wallet(
                wallet_uid = kwargs.get('wallet_uid'),
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
                'message': 'Wallet deleted successfully.'
            },
            status=status.HTTP_201_CREATED
        )