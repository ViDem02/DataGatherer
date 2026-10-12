from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.decorators import api_view

from functions_api.functions.stream_create_matrix.logic import stream_create_matrix
from functions_api.functions.use_default_crop.logic import apply_default_crop_to_target_image

from storage_api.models.image_models import ImgCrop, Image
from storage_api.models.project_models import Project
from storage_api.serializers.image_serializers import ImgCropSerializer
from rest_framework import generics
from django.http import HttpResponse, StreamingHttpResponse


class StreamCreateMatrixViewSet(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        response = StreamingHttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=matrix.csv'

        return stream_create_matrix(instance, response)
