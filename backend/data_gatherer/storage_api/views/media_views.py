import mimetypes
from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, HttpResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from data_gatherer.authentication import CookieJWTAuthentication
from storage_api.models.image_models import Image

# Uploaded files must never be able to run as a page on this origin
MEDIA_CSP = "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; sandbox"


class ProtectedMediaView(APIView):
    """Serves uploaded files to their owner only. Staff can open every file, as they can in the admin."""
    # The admin session is accepted too, so the file links in the admin keep working
    authentication_classes = [CookieJWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_path):
        if not request.user.is_staff and not Image.objects.filter(file=file_path, author=request.user).exists():
            raise Http404

        try:
            if not default_storage.exists(file_path):
                raise Http404
        except SuspiciousFileOperation:
            raise Http404

        content_type, _ = mimetypes.guess_type(file_path)
        if settings.MEDIA_ACCEL_REDIRECT_LOCATION:
            # nginx sends the file from its internal location now that the request is authorized
            response = HttpResponse(content_type=content_type or 'application/octet-stream')
            response['X-Accel-Redirect'] = settings.MEDIA_ACCEL_REDIRECT_LOCATION + quote(file_path)
        else:
            response = FileResponse(default_storage.open(file_path), content_type=content_type)

        response['Cache-Control'] = 'private, max-age=3600'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Security-Policy'] = MEDIA_CSP
        return response
