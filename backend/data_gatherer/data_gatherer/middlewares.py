from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
JWT_authenticator = JWTAuthentication()

from django.contrib.auth.models import AnonymousUser


class UserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path: str = request.META["PATH_INFO"][1:]
        user = request.user if request.user is not None else AnonymousUser
        try:
            auth_response = JWT_authenticator.authenticate(request)
        except InvalidToken as e:
            print("token invalid")
            auth_response = None
        if auth_response is not None:
            user, token = auth_response

        #if (not user.is_authenticated) and (not path.startswith(settings.PUBLIC_PATH_STARTS_WITH)):
        #    print("middleware blocked.")
        #    response = Response(
        #        status=status.HTTP_403_FORBIDDEN
        #    )
        #    response.accepted_renderer = JSONRenderer()
        #    response.accepted_media_type = "application/json"
        #    response.renderer_context = {}
        #    response.render()
        #    return response
        return self.get_response(request)
