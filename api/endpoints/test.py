from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def test_endpoint(request):
    """Test endpoint that returns 'Hello World'"""
    return Response({"message": "Hello World"})

