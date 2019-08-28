# from django.shortcuts import render

from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, AuthTokenSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
# Create your views here.

class CreateUserView(generics.CreateAPIView):
    """ create a new user """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UpdateUserView(generics.RetrieveUpdateAPIView):
    """ update the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
