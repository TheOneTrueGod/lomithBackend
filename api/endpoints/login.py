from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


@api_view(['POST'])
def login_endpoint(request):
    """
    Login endpoint that returns an access token valid for 24 hours.
    Accepts any username/password and returns token for hardcoded user.
    """
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    
    # Hardcoded authentication - accept any credentials
    if username and password:
        # Get hardcoded user for token generation
        # This user should be created during initial setup
        try:
            user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            return Response(
                {"error": "System not initialized. Please run migrations and create test user."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Generate JWT token (valid for 24 hours as configured)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return Response({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 86400  # 24 hours in seconds
        }, status=status.HTTP_200_OK)
    
    return Response(
        {"error": "Username and password are required"},
        status=status.HTTP_400_BAD_REQUEST
    )

