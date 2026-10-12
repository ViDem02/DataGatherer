from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.decorators import api_view
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist


from functions_api.functions.use_default_crop.logic import apply_default_crop_to_target_image
from functions_api.functions.use_default_crop.serializer import Serializer
from storage_api.models.image_models import ImgCrop, Image
from storage_api.serializers.image_serializers import ImgCropSerializer
from rest_framework import generics
from storage_api.models.project_models import *


class UseDefaultCropView(generics.CreateAPIView):
    queryset = []
    serializer_class = Serializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        fieldName = ser.validated_data['fieldName']
        targetImage = ser.validated_data['targetImage']
        project = ser.validated_data['project']

        try:
            default_crop_obj:ProjectDefaultCrop = ProjectDefaultCrop.objects.get(
                fieldName=fieldName,
                project=project
            )
        except MultipleObjectsReturned:
            return Response('Esiste più di un taglio di default',
                            HTTP_500_INTERNAL_SERVER_ERROR)  # Has been tested not to be the case
        except ObjectDoesNotExist:
            return Response('Non esiste un taglio di default',
                            HTTP_404_NOT_FOUND)

        new_cut = apply_default_crop_to_target_image(targetImage, default_crop_obj)

        return Response(ImgCropSerializer(instance=new_cut).data, HTTP_200_OK)