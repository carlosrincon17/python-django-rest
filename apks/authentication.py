from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token


class TokenAuth(authentication.BaseAuthentication):

    def authenticate(self, request):
        token = get_token(request)
        if not token:
            raise exceptions.AuthenticationFailed('No valid Token')
        try:
            token = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('No valid Token')
        return token, None


def get_token(request):
    return request.META.get('HTTP_AUTHORIZATION')