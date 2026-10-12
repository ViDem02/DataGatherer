import os

from PIL import Image as PILImage
from rest_framework import serializers

# Uploads are served from the app's own origin, so only real raster images are accepted.
ALLOWED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.webp']
ALLOWED_IMAGE_FORMATS = ['PNG', 'JPEG', 'WEBP']

PERCENT_FIELD_KWARGS = {'min_value': 0, 'max_value': 100}


def validate_image_upload(file):
    extension = os.path.splitext(file.name)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise serializers.ValidationError(
            "%s: estensione non consentita (ammesse: %s)" % (file.name, ', '.join(ALLOWED_IMAGE_EXTENSIONS))
        )
    try:
        with PILImage.open(file) as img:
            img_format = img.format
            img.verify()
    except Exception:
        raise serializers.ValidationError("%s: non è un'immagine valida" % file.name)
    finally:
        file.seek(0)
    if img_format not in ALLOWED_IMAGE_FORMATS:
        raise serializers.ValidationError("%s: formato immagine non consentito" % file.name)
    return file


class OwnedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Only accepts related objects authored by the requesting user."""

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.context.get('request')
        if request is None:
            return queryset.none()
        return queryset.filter(author=request.user)


class OwnedModelSerializer(serializers.ModelSerializer):
    serializer_related_field = OwnedPrimaryKeyRelatedField
