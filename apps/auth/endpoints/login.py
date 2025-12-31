from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

# Demo user credentials
DEMO_EMAIL = "john@example.com"
DEMO_PASSWORD = "T3stUs4rP4ss"


@api_view(["POST"])
def login_endpoint(request):
    """
    Login endpoint that returns an access token valid for 24 hours.
    Accepts demo user credentials and returns a real JWT token.
    """
    username = request.data.get("username", "")
    password = request.data.get("password", "")

    # Check if credentials match demo user
    if username == DEMO_EMAIL and password == DEMO_PASSWORD:
        # Get or create demo user for token generation
        try:
            demo_user = User.objects.get(username="john")
        except User.DoesNotExist:
            # Create demo user if it doesn't exist
            demo_user = User.objects.create_user(
                username="john",
                email=DEMO_EMAIL,
                password=DEMO_PASSWORD
            )
        
        # Generate real JWT token (valid for 24 hours as configured)
        refresh = RefreshToken.for_user(demo_user)
        access_token = str(refresh.access_token)
        
        return Response(
            {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 86400,  # 24 hours in seconds
            },
            status=status.HTTP_200_OK,
        )

    # Hardcoded authentication - accept any credentials
    if username and password:
        # Get hardcoded user for token generation
        # This user should be created during initial setup
        try:
            user = User.objects.get(username="testuser")
        except User.DoesNotExist:
            return Response(
                {
                    "error": "System not initialized. Please run migrations and create test user."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate JWT token (valid for 24 hours as configured)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 86400,  # 24 hours in seconds
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED
    )
