from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *

from functions_api.functions.extend_network_from_image.logic import extend_network_from_image
from functions_api.functions.extend_network_from_image.serializer import Serializer
from storage_api.models.image_models import ImgCrop, Image, ImgData


class ExtendNetworkFromImageView(generics.CreateAPIView):
    queryset = []
    serializer_class = Serializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        target_image: Image = ser.validated_data['targetImage']

        try:
            username_data:ImgData = ImgData.objects.get(
                fieldName='Username',
                image=target_image,
            )
        except ObjectDoesNotExist or MultipleObjectsReturned:
            return Response("Non esiste alcun dato Username nel sistema!", HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned:
            return Response("Esiste più di un dato Username nel sistema!", HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            hashtags_data:ImgData = ImgData.objects.get(
                fieldName='Hashtags',
                image=target_image,
            )
        except ObjectDoesNotExist:
            return Response("Non esiste alcun dato Hashtags nel sistema!", HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned:
            return Response("Esiste più di un dato Hashtags nel sistema!", HTTP_500_INTERNAL_SERVER_ERROR)

        extend_network_from_image(
            username_data.value,
            hashtags_data.value,
            target_image.project,
            target_image
        )

        return Response("{}", HTTP_200_OK)
