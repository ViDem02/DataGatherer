import io

from django.core.management import call_command
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from services.compute_index import compute_index


class ComputeIndex(generics.RetrieveAPIView):
    # The index is built from every user's data and is expensive to compute: staff only.
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        compute_index()
        response = Response(
            status=status.HTTP_200_OK,
            data="computed"
        )
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()

        return response
