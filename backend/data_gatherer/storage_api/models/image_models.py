import traceback

from django.db import models
from rest_framework import status
from rest_framework.exceptions import ValidationError
from functions_api.functions.upload_pictures.logic import check_similarity_between_project_images
from services.ocr_services import read_text_from_img, special_username_text_from_img
from django.contrib.auth.models import User

from services.suggestion_service import get_suggestion


class Image(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    file = models.FileField(upload_to='imgs/', unique=True)
    userId = models.IntegerField()
    isDataGathered = models.BooleanField(default=False)
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE
    )
    average_hash = models.CharField(max_length=4000, blank=True, null=True)
    isSimilarTo = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ['project', 'userId']
        ordering = ['-userId']

    def __str__(self):
        return "PRJ: %s, image %s" % (self.project, self.userId)


class ImgData(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    fieldName = models.CharField(max_length=30)
    value = models.TextField(max_length=5000)

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['fieldName', 'image']


class ImgCrop(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    fieldName = models.CharField(max_length=30)
    topPercent = models.FloatField()
    leftPercent = models.FloatField()
    heightPercent = models.FloatField()
    widthPercent = models.FloatField()
    recognizedText = models.TextField(max_length=10000, blank=True)
    reviewedText = models.TextField(max_length=10000, blank=True, null=True)  # TODO To be deleted
    suggestedText = models.TextField(max_length=10000, blank=True, null=True)

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE
    )

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        try:
            self.recognizedText = special_username_text_from_img(
                self.image.file.path,
                self.topPercent,
                self.leftPercent,
                self.widthPercent,
                self.heightPercent
            ) if self.fieldName == "Username" else read_text_from_img(
                self.image.file.path,
                self.topPercent,
                self.leftPercent,
                self.widthPercent,
                self.heightPercent
            )
            if self.fieldName == "Username":
                self.suggestedText = get_suggestion(self.recognizedText)
        except Exception: #TODO da migliorare in futuro
            print(traceback.format_exc())
            raise ValidationError(
               'Errore nel riconoscimento del testo',
               status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        ImgCrop.objects.filter(
            image=self.image,
            fieldName=self.fieldName,
        ).delete()

        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __str__(self):
        return "crop %s of img %s" % (self.id, self.image_id)
