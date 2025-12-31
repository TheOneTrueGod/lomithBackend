from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


@api_view(["POST"])
def create_user_endpoint(request):
    """
    Create a new user endpoint.
    Accepts username, email, and password and creates a new user account.
    Returns a JWT access token upon successful creation.
    """
    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")

    # Validate required fields
    if not username:
        return Response(
            {"error": "Username is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not password:
        return Response(
            {"error": "Password is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"error": "Invalid email format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate password length (Django's default minimum is usually enforced)
    if len(password) < 8:
        return Response(
            {"error": "Password must be at least 8 characters long"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Generate JWT token for the newly created user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {
                "message": "User created successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 86400,  # 24 hours in seconds
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to create user: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

