from rest_framework import serializers
from storage_api.models.image_models import *
from storage_api.serializers.common_serializers import OwnedModelSerializer, validate_image_upload, \
    PERCENT_FIELD_KWARGS


class ImageSerializer(OwnedModelSerializer):
    image_file_url = serializers.SerializerMethodField()
    is_similar_to_user_id = serializers.SerializerMethodField()

    def get_is_similar_to_user_id(self, obj:Image):
        if obj.isSimilarTo is None: return None
        return obj.isSimilarTo.userId

    def get_image_file_url(self, obj: Image):
        return obj.file.url

    def validate_file(self, value):
        return validate_image_upload(value)

    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ['author']


class ImgDataSerializer(OwnedModelSerializer):
    class Meta:
        model = ImgData
        fields = '__all__'
        read_only_fields = ['author']


class ImgCropSerializer(OwnedModelSerializer):
    class Meta:
        model = ImgCrop
        fields = '__all__'
        read_only_fields = ['author']
        extra_kwargs = {
            'topPercent': PERCENT_FIELD_KWARGS,
            'leftPercent': PERCENT_FIELD_KWARGS,
            'heightPercent': PERCENT_FIELD_KWARGS,
            'widthPercent': PERCENT_FIELD_KWARGS,
        }
