from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from storage_api.models.project_models import *

from storage_api.serializers.project_serializers import *
from django_filters import rest_framework as filters

from storage_api.views.common.common_views import OwnedInstancesCompleteModelViewSet


class ProjectViewSet(OwnedInstancesCompleteModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = []


class ProjectDefaultCropViewSet(OwnedInstancesCompleteModelViewSet):
    queryset = ProjectDefaultCrop.objects.all()
    serializer_class = ProjectDefaultCropSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['project', 'fieldName']

    # The old default is deleted before the new one is validated: one transaction, so a failure keeps the old one
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer:ProjectDefaultCropSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        ProjectDefaultCrop.objects.filter(
            project=serializer.data['project'],
            fieldName=serializer.data['fieldName'],
            project__author=request.user
        ).delete()

        return super().create(request, *args, **kwargs)




