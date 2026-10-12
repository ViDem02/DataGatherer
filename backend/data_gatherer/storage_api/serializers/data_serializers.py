from rest_framework import serializers
from storage_api.models.data_models import *
from storage_api.serializers.common_serializers import OwnedModelSerializer


class HashtagSerializer(OwnedModelSerializer):
    class Meta:
        model = Hashtag
        fields = '__all__'
        read_only_fields = ['author']


class IGUserSerializer(OwnedModelSerializer):
    class Meta:
        model = IGUser
        fields = '__all__'
        read_only_fields = ['author']


class UserHashtagUseSerializer(OwnedModelSerializer):
    igUser = IGUserSerializer()
    hashtag = HashtagSerializer()

    class Meta:
        model = UserHashtagUse
        fields = '__all__'
        read_only_fields = ['author']


