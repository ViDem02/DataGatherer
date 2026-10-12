from storage_api.models.image_models import *

from storage_api.serializers.image_serializers import ImageSerializer, ImgCropSerializer, ImgDataSerializer
from django_filters import rest_framework as filters

from storage_api.views.common.common_views import OwnedInstancesCompleteModelViewSet


class ImageViewSet(OwnedInstancesCompleteModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['project', 'isDataGathered']


class ImgCropViewSet(OwnedInstancesCompleteModelViewSet):
    queryset = ImgCrop.objects.all()
    serializer_class = ImgCropSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['image', 'fieldName']

    def create(self, request, *args, **kwargs):
        img_id = request.data['image']
        field_name = request.data['fieldName']

        ImgCrop.objects.filter(image_id=img_id, image__author=request.user).filter(fieldName=field_name).delete()

        return super().create(request, *args, **kwargs)


class ImgDataViewSet(OwnedInstancesCompleteModelViewSet):
    queryset = ImgData.objects.all()
    serializer_class = ImgDataSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_fields = ['image', 'fieldName']

    def create(self, request, *args, **kwargs):
        serializer: ImgDataSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        ImgData.objects.filter(
            fieldName=serializer.data['fieldName'],
            image_id=int(serializer.data['image']),
            image__author=request.user
        ).delete()

        return super().create(request, *args, **kwargs)


