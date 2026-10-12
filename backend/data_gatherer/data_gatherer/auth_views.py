from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, Throttled
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from data_gatherer.authentication import set_auth_cookies, delete_auth_cookies


class CookieTokenObtainView(TokenObtainPairView):
    """Logs in: the tokens are only ever sent as HttpOnly cookies, never in the response body."""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except AuthenticationFailed:
            # Set by django-axes when this username/IP pair is locked out
            if getattr(request, 'axes_locked_out', False):
                raise Throttled(detail='Troppi tentativi di accesso falliti: riprova più tardi.')
            raise

        response = Response({'username': serializer.user.get_username()}, status=status.HTTP_200_OK)
        set_auth_cookies(response, serializer.validated_data['access'], serializer.validated_data['refresh'])
        # The app sends this token back in the X-CSRFToken header with every cookie-authenticated request
        get_token(request)
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Issues a new access token (and rotates the refresh token) from the refresh cookie."""

    def post(self, request, *args, **kwargs):
        raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if raw_refresh is None:
            raise InvalidToken('Refresh token mancante')

        serializer = self.get_serializer(data={'refresh': raw_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = Response({}, status=status.HTTP_200_OK)
        set_auth_cookies(response, serializer.validated_data['access'], serializer.validated_data.get('refresh'))
        get_token(request)
        return response


class LogoutView(APIView):
    """Revokes the refresh token and deletes the auth cookies (page scripts can't delete HttpOnly cookies)."""
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if raw_refresh is not None:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass  # Already expired or revoked: nothing left to revoke

        response = Response(status=status.HTTP_204_NO_CONTENT)
        delete_auth_cookies(response)
        return response
