from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from axes.backends import AxesStandaloneBackend


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads the access token from the Authorization header (API clients) or from the
    HttpOnly cookie set at login (the browser app), so page scripts never see a token.
    Browsers attach cookies on their own, so cookie-authenticated requests must pass the CSRF check.
    """

    def authenticate(self, request):
        result = self.authenticate_token(request)
        if result is not None and self.get_header(request) is None:
            self.enforce_csrf(request)
        return result

    def authenticate_token(self, request):
        """authenticate() without the CSRF check: only for telling whether a request is logged in."""
        if self.get_header(request) is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def enforce_csrf(self, request):
        # Same check as rest_framework.authentication.SessionAuthentication
        def dummy_get_response(request):
            return None

        check = CSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)


def set_auth_cookies(response, access=None, refresh=None):
    cookie_kwargs = {
        'httponly': True,
        'secure': settings.SECURE_COOKIES,
        'samesite': settings.AUTH_COOKIE_SAMESITE,
    }
    if access is not None:
        response.set_cookie(
            settings.AUTH_COOKIE_ACCESS, access, path='/',
            max_age=int(jwt_settings.ACCESS_TOKEN_LIFETIME.total_seconds()), **cookie_kwargs
        )
    if refresh is not None:
        # Only the token endpoints ever need the refresh token
        response.set_cookie(
            settings.AUTH_COOKIE_REFRESH, refresh, path=settings.AUTH_COOKIE_REFRESH_PATH,
            max_age=int(jwt_settings.REFRESH_TOKEN_LIFETIME.total_seconds()), **cookie_kwargs
        )


def delete_auth_cookies(response):
    response.delete_cookie(settings.AUTH_COOKIE_ACCESS, path='/', samesite=settings.AUTH_COOKIE_SAMESITE)
    response.delete_cookie(settings.AUTH_COOKIE_REFRESH, path=settings.AUTH_COOKIE_REFRESH_PATH,
                           samesite=settings.AUTH_COOKIE_SAMESITE)


def get_client_ip(request):
    """Client IP used for the login lockout (AXES_CLIENT_IP_CALLABLE)."""
    if settings.BEHIND_REVERSE_PROXY:
        # nginx overwrites X-Real-IP with the address it sees, so it can't be spoofed through it
        return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
    return request.META.get('REMOTE_ADDR')


class LoginLockoutBackend(AxesStandaloneBackend):
    """
    Refuses logins once too many attempts have failed (django-axes).
    Calls without a request (shell, scripts, tests) don't come from the network and are not counted.
    """

    def authenticate(self, request, *args, **kwargs):
        if request is None:
            return None
        return super().authenticate(request, *args, **kwargs)
