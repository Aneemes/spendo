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
    """
    UserLoginAPIView handles user login requests.
    This view provides a POST method to authenticate users based on their email and password.
    If authentication is successful, it returns user details and an access token, and sets a refresh token in the cookies.
    Attributes:
        UserLoginInputSerializer (class): Serializer for validating user login input data.
        UserLoginOutputSerializer (class): Serializer for formatting user login output data.
    Methods:
        post(request, *args, **kwargs):
            Handles the POST request to authenticate a user.
            Validates the input data, attempts to log in the user, and returns the appropriate response.
    """

    class UserLoginInputSerializer(serializers.Serializer):
        """
        Serializer for user login input.

        Fields:
            email (EmailField): The email address of the user. This field is write-only.
            password (CharField): The password of the user. This field is write-only.
        """
        email = serializers.EmailField(write_only=True)
        password = serializers.CharField(write_only=True)

    class UserLoginOutputSerializer(serializers.Serializer):
        """
        Serializer for user login output.

        Fields:
            full_name (str): The full name of the user. This field is read-only.
            username (str): The username of the user. This field is read-only.
            access_token (str): The access token for the user session. This field is read-only.
        """
        full_name = serializers.CharField(read_only=True)
        username = serializers.CharField(read_only=True)
        access_token = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user login.

        This method validates the input data using UserLoginInputSerializer,
        attempts to log in the user, and returns an appropriate response.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object containing the login result.

        Raises:
            DRFValidationError: If the input data is invalid according to DRF validation.
            DjangoValidationError: If the input data is invalid according to Django validation.
        """
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
    """
    UserLogoutAPIView handles the user logout process by invalidating the refresh token.
    Attributes:
        permission_classes (list): List of permission classes that the view requires.
    Methods:
        post(request, *args, **kwargs):
            Handles the POST request to log out the user by blacklisting the refresh token.
            Deletes the refresh token cookie from the response.
            Args:
                request (Request): The request object containing the refresh token in cookies.
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.
            Returns:
                Response: A response object indicating the success or failure of the logout process.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request,  *args, **kwargs):
        """
        Handle POST request to log out a user by blacklisting the refresh token.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A Response object indicating the result of the logout operation.

        Raises:
            KeyError: If the refresh token is not found in the cookies.
            Exception: For any other exceptions that occur during the logout process.
        """
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
    """
    RotateAccessTokenAPIView is an API view that handles the rotation of access tokens.
    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to refresh the access token using the refresh token stored in cookies.
            If the refresh token is present and valid, a new access token is generated and returned in the response.
            If the refresh token is not present, an unauthorized response is returned.
        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            Response: A Response object containing the new access token if the refresh token is valid,
                      or an error message if the refresh token is missing or invalid.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to refresh access token using the refresh token from cookies.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A Response object containing the new access token if the refresh token is valid,
                      otherwise an error message indicating the absence of the refresh token.
        """
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
    """
    ForgotPasswordAPIView handles the password reset request by sending a password reset email to the user.
    Methods:
        post(request, *args, **kwargs):
            Handles the POST request to send a password reset email.
            Validates the input email and sends the reset email if the email is valid.
        Inner Classes:
            ForgotPasswordInputSerializer(serializers.Serializer):
                Serializer for validating the input email.
    """
    
    class ForgotPasswordInputSerializer(serializers.Serializer):
        """
        Serializer for handling forgot password input.

        Fields:
            email (EmailField): The email address of the user requesting a password reset.
        """
        email = serializers.EmailField()
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to initiate the forgot password process.
        This method validates the input data using the ForgotPasswordInputSerializer,
        attempts to send a password reset email, and returns an appropriate response
        based on the success or failure of the email sending process.
        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            Response: A DRF Response object containing the success status and message.
        """
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
    """
    ResetPasswordAPIView handles the password reset process for a user.
    This view expects a POST request with the following data:
    - username: The username of the user requesting the password reset.
    - token: The token provided for password reset verification.
    - password: The new password to be set.
    - confirm_password: Confirmation of the new password.
    The view performs the following actions:
    1. Validates the input data using ResetPasswordInputSerializer.
    2. Attempts to reset the password using the reset_password function.
    3. Returns a success response if the password is reset successfully.
    4. Returns an error response if there are validation errors or other issues.
    Responses:
    - 200 OK: Password reset successfully.
    - 400 Bad Request: Validation error or other issues with the request data.
    """

    class ResetPasswordInputSerializer(serializers.Serializer):
        """
        Serializer for handling password reset input.

        Fields:
            username (str): The username of the user requesting the password reset.
            token (str): The token provided for password reset verification.
            password (str): The new password to be set.
            confirm_password (str): Confirmation of the new password.
        """
        username = serializers.CharField()
        token = serializers.CharField()
        password = serializers.CharField()
        confirm_password = serializers.CharField()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to reset the user's password.
        This method validates the input data using the ResetPasswordInputSerializer,
        attempts to reset the password, and returns an appropriate response.
        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            Response: A DRF Response object containing the success status and message.
        Raises:
            DRFValidationError: If the input data is invalid according to DRF validation.
            DjangoValidationError: If the input data is invalid according to Django validation.
        """
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
    """
    API view to handle password change requests for authenticated users.
    This view requires the user to be authenticated and provides an endpoint
    to change the user's password. The request must include the old password,
    new password, and confirmation of the new password.
    Attributes:
        permission_classes (list): List of permission classes that are required
            to access this view. In this case, the user must be authenticated.
    Classes:
        ChangePasswordInputSerializer (serializers.Serializer): Serializer class
            to validate the input data for changing the password. It includes
            fields for old_password, new_password, and confirm_password.
    Methods:
        post(request, *args, **kwargs): Handles the POST request to change the
            user's password. Validates the input data and attempts to change the
            password. Returns a success message if the password is changed
            successfully, otherwise returns an error message.
    """
    permission_classes = [IsAuthenticated]

    class ChangePasswordInputSerializer(serializers.Serializer):
        """
        Serializer for handling password change input.

        Fields:
            old_password (str): The current password of the user. This field is write-only.
            new_password (str): The new password that the user wants to set. This field is write-only.
            confirm_password (str): Confirmation of the new password. This field is write-only.
        """
        old_password = serializers.CharField(write_only=True)
        new_password = serializers.CharField(write_only=True)
        confirm_password = serializers.CharField(write_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to change the user's password.

        This method validates the input data using the ChangePasswordInputSerializer.
        If the data is valid, it attempts to change the user's password using the
        change_password function. If any validation errors occur, it returns a
        response with the appropriate error message and a 400 status code. If the
        password is changed successfully, it returns a success message with a 200
        status code.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object containing the success status and message.
        """
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