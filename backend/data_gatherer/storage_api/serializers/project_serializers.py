from rest_framework import serializers

from storage_api.models.image_models import Image
from storage_api.models.data_models import Hashtag, IGUser, UserHashtagUse
from storage_api.models.project_models import *
from storage_api.serializers.common_serializers import OwnedModelSerializer, PERCENT_FIELD_KWARGS


class ProjectSerializer(OwnedModelSerializer):
    are_all_images_analyzed = serializers.SerializerMethodField()
    next_image_to_analyze = serializers.SerializerMethodField()
    nr_hashtags = serializers.SerializerMethodField()
    nr_users = serializers.SerializerMethodField()

    def get_nr_hashtags(self, obj:Project):
        return UserHashtagUse.objects.filter(project=obj).values_list('hashtag__content', flat=True).distinct().count()

    def get_nr_users(self, obj:Project):
        return UserHashtagUse.objects.filter(project=obj).values_list('igUser__name', flat=True).distinct().count()

    def get_are_all_images_analyzed(self, obj:Project):
        return Image.objects.filter(project=obj, isDataGathered=False).count() == 0

    def get_next_image_to_analyze(self, obj:Project):
        data = Image.objects.filter(project=obj, isDataGathered=False).last()
        if data is None:
            return None
        return data.id

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['author']
        

class ProjectDefaultCropSerializer(OwnedModelSerializer):

    class Meta:
        model = ProjectDefaultCrop
        fields = '__all__'
        read_only_fields = ['author']
        extra_kwargs = {
            'topPercent': PERCENT_FIELD_KWARGS,
            'leftPercent': PERCENT_FIELD_KWARGS,
            'heightPercent': PERCENT_FIELD_KWARGS,
            'widthPercent': PERCENT_FIELD_KWARGS,
        }

