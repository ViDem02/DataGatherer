from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from data_gatherer.authentication import CookieJWTAuthentication

JWT_authenticator = CookieJWTAuthentication()


class UserMiddleware:
    """Refuses every request outside the public paths that doesn't carry a valid login token."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path: str = request.META["PATH_INFO"][1:]

        if not path.startswith(settings.PUBLIC_PATH_STARTS_WITH) and not self._is_logged_in(request):
            print("middleware blocked.")
            response = Response(
                status=status.HTTP_401_UNAUTHORIZED
            )
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()
            return response
        return self.get_response(request)

    @staticmethod
    def _is_logged_in(request):
        # Django session: staff browsing the admin, which links to uploaded files
        if request.user.is_authenticated:
            return True
        try:
            return JWT_authenticator.authenticate_token(request) is not None
        except AuthenticationFailed:
            return False
