import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from storage_api.models.image_models import Image
from storage_api.models.project_models import Project

pre_path = os.environ.get('TEST_PRE_PATH', default='')


class Authentication(TestCase):
    def setUp(self):
        self.anne = User.objects.create_user(
            username="anne",
            email="giacomo@gmail.com",
            password="giacomogiacomo"
        )
        self.bob = User.objects.create_user(
            username="bob",
            email="giaco@gmail.com",
            password="giacomogiacomo"
        )

    def test_authentication_is_successful(self):
        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.anne.username,
            'password': 'giacomogiacomo'
        })
        # Tokens are only handed out as HttpOnly cookies, never in the body
        assert 'access' in auth_response.cookies
        assert 'refresh' in auth_response.cookies
        assert auth_response.cookies['access']['httponly']
        assert 'access' not in auth_response.json()
        assert auth_response.status_code == 200

    def test_refresh_mechanism(self):
        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.anne.username,
            'password': 'giacomogiacomo'
        })
        # The client sends back the refresh cookie it got at login
        refresh_response = c.post(pre_path + '/a/token/refresh/')
        assert refresh_response.status_code == 200


class OwnedInstancesCompleteModelViewSet(TestCase):

    def setUp(self):
        self.anne = User.objects.create_user(
            username="anne",
            email="giacomo@gmail.com",
            password="giacomogiacomo"
        )
        self.bob = User.objects.create_user(
            username="bob",
            email="giaco@gmail.com",
            password="giacomogiacomo"
        )

    def test_author_is_added_to_object_created(self):
        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.anne.username,
            'password': "giacomogiacomo"
        })
        token = auth_response.cookies["access"].value

        response = c.post(pre_path + '/b/storage_api/projects/', {
            'name': 'prj_a'
        }, headers={
            'Authorization': 'Bearer %s' % token
        })

        assert response.status_code == 201

        assert response.json()['author'] == self.anne.pk

    def test_author_can_only_see_own_instances(self):
        Project.objects.all().delete()

        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.anne.username,
            'password': "giacomogiacomo"
        })
        token_anne = auth_response.cookies["access"].value

        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.bob.username,
            'password': "giacomogiacomo"
        })
        token_bob = auth_response.cookies["access"].value

        c.post(pre_path + '/b/storage_api/projects/', {
            'name': 'prj_a'
        }, headers={
            'Authorization': 'Bearer %s' % token_anne
        })

        c.post(pre_path + '/b/storage_api/projects/', {
            'name': 'prj_a'
        }, headers={
            'Authorization': 'Bearer %s' % token_bob
        })

        raw_res_anne = c.get(pre_path + '/b/storage_api/projects/', headers={
            'Authorization': 'Bearer %s' % token_anne
        })
        raw_res_bob = c.get(pre_path + '/b/storage_api/projects/', headers={
            'Authorization': 'Bearer %s' % token_bob
        })
        import json

        res_anne = json.loads(raw_res_anne.content)
        assert len(res_anne) == 1
        assert res_anne[0]['author'] == self.anne.pk

        res_bob = json.loads(raw_res_bob.content)
        assert len(res_bob) == 1
        assert res_bob[0]['author'] == self.bob.pk

    def test_user_cannot_crud_others_data(self):
        Project.objects.all().delete()

        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.anne.username,
            'password': "giacomogiacomo"
        })
        token_anne = auth_response.cookies["access"].value

        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.bob.username,
            'password': "giacomogiacomo"
        })
        token_bob = auth_response.cookies["access"].value

        c.post(pre_path + '/b/storage_api/projects/', {
            'name': 'prj_a'
        }, headers={
            'Authorization': 'Bearer %s' % token_anne
        })

        c.post(pre_path + '/b/storage_api/projects/', {
            'name': 'prj_a'
        }, headers={
            'Authorization': 'Bearer %s' % token_bob
        })

        prj_anne = Project.objects.get(author=self.anne)

        res = c.put(pre_path + '/b/storage_api/projects/%s/' % prj_anne.pk, {
            'author': self.anne.pk,
            'name': 'sussss'
        }, headers={
            'Authorization': 'Bearer %s' % token_bob
        }, content_type='application/json')

        assert res.status_code == 404

        res = c.delete(pre_path + '/b/storage_api/projects/%s/' % prj_anne.pk, headers={
            'Authorization': 'Bearer %s' % token_bob
        })

        assert res.status_code == 404





class HashtagViewSetTestCase(TestCase):
    pass


class IGUserViewSetTestCase(TestCase):
    pass


class UserHashtagUseViewSetTestCase(TestCase):
    pass


class ImageViewSetTestCase(TestCase):
    pass


class ImgCropViewSetTestCase(TestCase):

    def setUp(self):
        from django.conf import settings

        User.objects.create_user(
            email="test@test.it",
            username='test',
            password='test',
        )
        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': 'test',
            'password': 'test',
        })
        self.token = auth_response.cookies["access"].value
        self.project = Project.objects.create(
            name='Test',
            author=authenticate(
                username="test",
                password='test'
            )
        )

        with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
            _file = SimpleUploadedFile('test_screenshot', infile.read())
            self.image = Image.objects.create(
                file=_file,
                userId=0,
                isDataGathered=False,
                project=self.project,
                average_hash=None,
                isSimilarTo=None,
                author=authenticate(
                    username="test",
                    password='test'
                )
            )

    def tearDown(self):
        self.image.file.delete()
        self.image.delete()

    def test_creation_without_pre_existing_entities(self):
        c = Client()

        response = c.post(pre_path + '/b/storage_api/img_crops/', {
            'fieldName': 'Username',
            'topPercent': 0,
            'leftPercent': 0,
            'heightPercent': 100,
            'widthPercent': 50.55555555,
            'recognizedText': '',
            'image': self.image.pk,
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201

    def test_creation_with_pre_existing_entities(self):
        c = Client()

        c.post(pre_path + '/b/storage_api/img_crops/', {
            'fieldName': 'Username',
            'topPercent': 0,
            'leftPercent': 0,
            'heightPercent': 100,
            'widthPercent': 50.55555555,
            'recognizedText': '',
            'image': self.image.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        response = c.post(pre_path + '/b/storage_api/img_crops/', {
            'fieldName': 'Username',
            'topPercent': 0,
            'leftPercent': 0,
            'heightPercent': 10,
            'widthPercent': 50.55555555,
            'recognizedText': '',
            'image': self.image.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201


class ImgDataViewSetTestCase(TestCase):

    def setUp(self):
        from django.conf import settings

        User.objects.create_user(
            email="test@test.it",
            username='test',
            password='test',
        )
        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': 'test',
            'password': 'test',
        })
        self.token = auth_response.cookies["access"].value
        self.project = Project.objects.create(
            name='Test',
            author=authenticate(
                username="test",
                password='test'
            )
        )

        with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
            _file = SimpleUploadedFile('test_screenshot', infile.read())
            self.image = Image.objects.create(
                file=_file,
                userId=0,
                isDataGathered=False,
                project=self.project,
                average_hash=None,
                isSimilarTo=None,
                author=authenticate(
                    username="test",
                    password='test'
                )
            )

    def tearDown(self):
        self.image.file.delete()
        self.image.delete()

    def test_creation_without_pre_existing_entities(self):
        c = Client()

        response = c.post(pre_path + '/b/storage_api/img_data/', {
            'fieldName': 'Username',
            'value': 'bubi',
            'image': self.image.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201

    def test_creation_with_pre_existing_entities(self):
        c = Client()

        response = c.post(pre_path + '/b/storage_api/img_data/', {
            'fieldName': 'Username',
            'value': 'bubi',
            'image': self.image.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201

        response = c.post(pre_path + '/b/storage_api/img_data/', {
            'fieldName': 'Username',
            'value': 'bubi',
            'image': self.image.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201

        response = c.post(pre_path + '/b/storage_api/img_data/', {
            'fieldName': 'Username',
            'value': 'bubidtfyvu',
            'image': self.image.pk
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201


class ProjectViewSetTestCase(TestCase):
    pass


class ProjectDefaultCropViewSetTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(
            email="test@test.it",
            username='test',
            password='test',
        )
        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': 'test',
            'password': 'test',
        })
        self.token = auth_response.cookies["access"].value
        self.project = Project.objects.create(
            name='Test',
            author=authenticate(
                username="test",
                password='test'
            )
        )

    def test_creation_without_pre_existing_entities_proj_default_crop(self):
        c = Client()

        response = c.post(pre_path + '/b/storage_api/prj_default_crop/', {
            'project': self.project.pk,
            'topPercent': 0,
            'leftPercent': 0,
            'heightPercent': 1,
            'widthPercent': 9.9999999,
            'fieldName': 'Bub',
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        print(response)

        assert response.status_code == 201

    def test_creation_with_pre_existing_entities(self):
        c = Client()

        response = c.post(pre_path + '/b/storage_api/prj_default_crop/', {
            'project': self.project.pk,
            'topPercent': 0,
            'leftPercent': 0,
            'heightPercent': 1,
            'widthPercent': 9.9999999,
            'fieldName': 'Bub',
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201

        response = c.post(pre_path + '/b/storage_api/prj_default_crop/', {
            'project': self.project.pk,
            'topPercent': 0,
            'leftPercent': 0,
            'heightPercent': 1,
            'widthPercent': 9.9999999,
            'fieldName': 'Bub',
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201

        response = c.post(pre_path + '/b/storage_api/prj_default_crop/', {
            'project': self.project.pk,
            'topPercent': 0,
            'leftPercent': 85,
            'heightPercent': 11,
            'widthPercent': 9.9999,
            'fieldName': 'Bub',
        }, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        assert response.status_code == 201
