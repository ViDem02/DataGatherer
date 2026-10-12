from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

from storage_api.models.data_models import *
from storage_api.models.image_models import *
from storage_api.models.project_models import *
import os
pre_path = os.environ.get('TEST_PRE_PATH', default='')


class UseDefaultCropTestCase(TestCase):

    def setUp(self):
        from django.conf import settings

        self.anne = User.objects.create_user(
            username="anne",
            email="giacomo@gmail.com",
            password="giacomogiacomo"
        )

        self.project = Project.objects.create(
            name='Test',
            author=self.anne,
        )

        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.anne.username,
            'password': "giacomogiacomo"
        })
        self.token = auth_response.cookies["access"].value

        with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
            _file = SimpleUploadedFile('test_screenshot', infile.read())
            self.image = Image.objects.create(
                file=_file,
                userId=0,
                isDataGathered=False,
                project=self.project,
                average_hash=None,
                isSimilarTo=None,
                author=self.anne,
            )

        with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
            _file = SimpleUploadedFile('test_screenshot', infile.read())
            self.image2 = Image.objects.create(
                file=_file,
                userId=2,
                isDataGathered=False,
                project=self.project,
                average_hash=None,
                isSimilarTo=None,
                author=self.anne,
            )

    def tearDown(self):
        UserHashtagUse.objects.filter(
            image=self.image
        ).delete()

        UserHashtagUse.objects.filter(
            image=self.image2
        ).delete()

        self.image.file.delete()
        self.image.delete()

        self.image2.file.delete()
        self.image2.delete()

    def test_with_no_default_in_existence(self):
        c = Client()
        response = c.post(pre_path + '/b/fx_api/default_crop/', {
            'fieldName': 'Username',
            'targetImage': self.image2.pk,
            'project': self.project.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 404

    def test_normal_operation(self):
        ProjectDefaultCrop.objects.create(
            project=self.project,
            topPercent=0,
            leftPercent=0,
            heightPercent=55,
            widthPercent=55,
            fieldName='Username',
            author=self.project.author,
        )

        ProjectDefaultCrop.objects.create(
            project=self.project,
            topPercent=0,
            leftPercent=0,
            heightPercent=100,
            widthPercent=100,
            fieldName='Hashtags',
            author=self.project.author,
        )

        c = Client()
        response = c.post(pre_path + '/b/fx_api/default_crop/', {
            'fieldName': 'Username',
            'targetImage': self.image2.pk,
            'project': self.project.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 200

        ImgCrop.objects.get(
            fieldName='Username',
            topPercent=0,
            leftPercent=0,
            heightPercent=55,
            widthPercent=55,
            image=self.image2
        )

        response = c.post(pre_path + '/b/fx_api/default_crop/', {
            'fieldName': 'Hashtags',
            'targetImage': self.image2.pk,
            'project': self.project.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 200

        ImgCrop.objects.get(
            fieldName='Hashtags',
            topPercent=0,
            leftPercent=0,
            heightPercent=100,
            widthPercent=100,
            image=self.image2
        )



