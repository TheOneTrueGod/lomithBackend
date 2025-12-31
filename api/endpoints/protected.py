from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_endpoint(request):
    """
    Protected endpoint that returns 'Welcome <user name>' if valid token,
    or 'Please login' if invalid token.
    """
    if request.user and request.user.is_authenticated:
        return Response({
            "message": f"Welcome {request.user.username}"
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "message": "Please login"
        }, status=status.HTTP_401_UNAUTHORIZED)

