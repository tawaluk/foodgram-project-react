from rest_framework import status
from rest_framework.response import Response


def validation_400(value):
    if not value:
        return Response(status=status.HTTP_400_BAD_REQUEST)
