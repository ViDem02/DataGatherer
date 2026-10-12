from rest_framework import serializers

from storage_api.models.image_models import Image
from storage_api.models.project_models import Project
from storage_api.serializers.common_serializers import OwnedPrimaryKeyRelatedField


class Serializer(serializers.Serializer):
    targetImage = OwnedPrimaryKeyRelatedField(queryset=Image.objects.all())