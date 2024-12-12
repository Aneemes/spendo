from django.db import transaction
from rest_framework import serializers, status
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from .services import (
    user_signup, user_login, send_forgot_password_email, reset_password, change_password
)


class UserSignUpAPIView(APIView):
    """
    UserSignUpAPIView is an API view that handles user registration.
    It accepts user details like full name, email, password, and confirm password,
    validates them, and creates a new user account. On successful signup, it returns
    the created user's details, along with an access token.

    Methods:
        post: Handles the POST request to sign up a user.
    """

    class UserSignUpInputSerializer(serializers.Serializer):
        """
        Serializer for validating user input during sign-up.
        
        Fields:
            full_name (str): The full name of the user.
            email (str): The email address of the user.
            password (str): The password for the user.
            confirm_password (str): The confirmation of the password.
        """
        full_name = serializers.CharField(write_only=True, required=True)
        email = serializers.EmailField(write_only=True, required=True)
        password = serializers.CharField(write_only=True, required=True)
        confirm_password = serializers.CharField(write_only=True, required=True)

    class UserSignUpOutputSerializer(serializers.Serializer):
        """
        Serializer for sending the response data after successful sign-up.
        
        Fields:
            full_name (str): The full name of the user.
            username (str): The username of the user.
            access_token (str): The access token for the user.
        """
        full_name = serializers.CharField(read_only=True)
        username = serializers.CharField(read_only=True)
        access_token = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to sign up a new user.
        
        Validates the input data, creates a user, and returns the response with 
        user details and an access token. If the input data is invalid, appropriate 
        error messages are returned.

        Args:
            request (Request): The HTTP request object containing the user input data.

        Returns:
            Response: A Response object containing the result of the sign-up process.
        """
        # Validate input data using the input serializer
        input_serializer = self.UserSignUpInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            # Call user_signup function to create a new user
            signup_details, refresh_token = user_signup(**input_serializer.validated_data)
        except DRFValidationError as e:
            # Handle custom DRF validation error
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DjangoValidationError as e:
            # Handle Django validation error
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serialize the user details and prepare the response
        output_serializer = self.UserSignUpOutputSerializer(signup_details)
        response = Response(
            {
                "success": True,
                "message": "User signup successful",
                "data": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

        # Set a refresh token as a secure cookie
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.REFRESH_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",
            secure=False,
        )

        return response


class UserLoginAPIView(APIView):

    class UserLoginInputSerializer(serializers.Serializer):
        email = serializers.EmailField(write_only=True)
        password = serializers.CharField(write_only=True)

    class UserLoginOutputSerializer(serializers.Serializer):
        full_name = serializers.CharField(read_only=True)
        username = serializers.CharField(read_only=True)
        access_token = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.UserLoginInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            login_details, refresh_token = user_login(
                **input_serializer.validated_data
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        output_serializer = self.UserLoginOutputSerializer(login_details)
        response = Response(
            {
                "success": True,
                "message": "User logged in successfully.",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.REFRESH_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",
            secure=False
        )
        return response

class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request,  *args, **kwargs):
        try:
            refresh = RefreshToken(request.COOKIES.get("refresh_token"))
            refresh.blacklist()
            response = Response(
                {
                    "success": True,
                    "message": "Logout Successfull."
                },
                status=status.HTTP_200_OK
            )
            response.delete_cookie("refresh_token")
            return response
        except KeyError:
            return Response(
                {
                    "success": False,
                    "message": "No refresh token: keyerror",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
class RotateAccessTokenAPIView(APIView):

    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is not None:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response(
                {
                    "success": True,
                    "message": "Token refreshed successfully.",
                    "data": {"access_token": access_token},
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "message": "No refresh token",
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
class ForgotPasswordAPIView(APIView):
    
    class ForgotPasswordInputSerializer(serializers.Serializer):
        email = serializers.EmailField()
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.ForgotPasswordInputSerializer(data= request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            email_sent_status = send_forgot_password_email(
                **input_serializer.validated_data
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": "Password reset email sent successfully."
            },
            status=status.HTTP_200_OK
        )
    
class ResetPasswordAPIView(APIView):

    class ResetPasswordInputSerializer(serializers.Serializer):
        username = serializers.CharField()
        token = serializers.CharField()
        password = serializers.CharField()
        confirm_password = serializers.CharField()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.ResetPasswordInputSerializer(serializers.Serializer)
        input_serializer.is_valid(raise_exception=True)

        try:
            password_reset_status = reset_password(
                **input_serializer.validated_data
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": "Password reset successfully."
            },
            status=status.HTTP_200_OK
        ) 

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class ChangePasswordInputSerializer(serializers.Serializer):
        old_password = serializers.CharField(write_only=True)
        new_password = serializers.CharField(write_only=True)
        confirm_password = serializers.CharField(write_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.ChangePasswordInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            password_change_status = change_password(
                **input_serializer.validated_data,
                user=request.user
            )
        except DRFValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": "Password changed successfully."
            },
            status=status.HTTP_200_OK
        )