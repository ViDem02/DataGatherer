import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

from storage_api.models.data_models import *
from storage_api.models.image_models import *
from storage_api.models.project_models import *
import os

pre_path = os.environ.get('TEST_PRE_PATH', default='')


class StreamCreateMatrix(TestCase):

    def setUp(self):
        from django.conf import settings

        self.anne = User.objects.create_user(
            username="anne",
            email="giacomo@gmail.com",
            password="giacomogiacomo"
        )

        c = Client()
        auth_response = c.post(pre_path + '/a/token/obtain/', {
            'username': self.anne.username,
            'password': "giacomogiacomo"
        })
        self.token = auth_response.cookies["access"].value

        self.project1 = Project.objects.create(
            name='Test',
            author=self.anne,
        )

        self.project2 = Project.objects.create(
            name='Test2',
            author=self.anne,
        )

        with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
            _file = SimpleUploadedFile('test_screenshot', infile.read())
            self.image = Image.objects.create(
                file=_file,
                userId=0,
                isDataGathered=False,
                project=self.project1,
                average_hash=None,
                isSimilarTo=None,
                author=self.anne
            )

        with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
            _file = SimpleUploadedFile('test_screenshot', infile.read())
            self.image2 = Image.objects.create(
                file=_file,
                userId=25,
                isDataGathered=False,
                project=self.project1,
                average_hash=None,
                isSimilarTo=None,
                author=self.anne
            )

    def tearDown(self):
        UserHashtagUse.objects.filter(
            image=self.image
        ).delete()

        self.image.file.delete()
        self.image.delete()

        UserHashtagUse.objects.filter(
            image=self.image2
        ).delete()

        self.image2.file.delete()
        self.image2.delete()

    def test_normal_operations(self):
        h_a = Hashtag.objects.create(
            project=self.project1,
            content='a',
            createdFromImage=self.image,
            author=self.anne
        )

        h_b = Hashtag.objects.create(
            project=self.project1,
            content='b',
            createdFromImage=self.image,
            author=self.anne
        )

        h_1 = Hashtag.objects.create(
            project=self.project2,
            content='1',
            createdFromImage=self.image,
            author=self.anne
        )

        h_2 = Hashtag.objects.create(
            project=self.project2,
            content='2',
            createdFromImage=self.image,
            author=self.anne
        )

        u_a = IGUser.objects.create(
            project=self.project1,
            name='usera',
            createdFromImage=self.image,
            author=self.anne
        )

        u_b = IGUser.objects.create(
            project=self.project1,
            name='userb',
            createdFromImage=self.image,
            author=self.anne
        )

        u_1 = IGUser.objects.create(
            project=self.project2,
            name='user1',
            createdFromImage=self.image,
            author=self.anne
        )

        UserHashtagUse.objects.create(  # u_a 1st use of h1
            project=self.project1,
            igUser=u_a,
            hashtag=h_a,
            image=self.image,
            author=self.anne
        )

        UserHashtagUse.objects.create(  # u_a 2nd use of h_a
            project=self.project1,
            igUser=u_a,
            hashtag=h_a,
            image=self.image2,
            author=self.anne
        )

        UserHashtagUse.objects.create(  # u_a 1st use of h_b
            project=self.project1,
            igUser=u_a,
            hashtag=h_b,
            image=self.image,
            author=self.anne
        )

        UserHashtagUse.objects.create(  # u_b 1st use of h_b
            project=self.project1,
            igUser=u_b,
            hashtag=h_b,
            image=self.image,
            author=self.anne
        )

        UserHashtagUse.objects.create(
            project=self.project2,
            igUser=u_1,
            hashtag=h_1,
            image=self.image,
            author=self.anne
        )

        UserHashtagUse.objects.create(
            project=self.project2,
            igUser=u_1,
            hashtag=h_2,
            image=self.image,
            author=self.anne
        )

        c = Client()
        response = c.get(pre_path + '/b/fx_api/matrix/%s/' % self.project1.pk, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        content = io.BytesIO(b"".join(response.streaming_content))
        wrapper = io.TextIOWrapper(content, encoding='utf-8')

        resulting_csv = wrapper.read()

        assert resulting_csv == ";usera;userb\na;2;0\nb;1;1\n"

    def test_export_matrix_with_no_data(self):
        c = Client()
        response = c.get(pre_path + '/b/fx_api/matrix/%s/' % self.project1.pk, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        content = io.BytesIO(b"".join(response.streaming_content))
        wrapper = io.TextIOWrapper(content, encoding='utf-8')

        resulting_csv = wrapper.read()

        assert resulting_csv == "%s%s%s" % (chr(34), chr(34), chr(10))

    def test_export_matrix_with_no_user_hashtag_uses(self):
        h_a = Hashtag.objects.create(
            project=self.project1,
            content='a',
            createdFromImage=self.image,
            author=self.anne
        )

        h_b = Hashtag.objects.create(
            project=self.project1,
            content='b',
            createdFromImage=self.image,
            author=self.anne
        )

        h_1 = Hashtag.objects.create(
            project=self.project2,
            content='1',
            createdFromImage=self.image,
            author=self.anne
        )

        h_2 = Hashtag.objects.create(
            project=self.project2,
            content='2',
            createdFromImage=self.image,
            author=self.anne
        )

        u_a = IGUser.objects.create(
            project=self.project1,
            name='usera',
            createdFromImage=self.image,
            author=self.anne
        )

        u_b = IGUser.objects.create(
            project=self.project1,
            name='userb',
            createdFromImage=self.image,
            author=self.anne
        )

        u_1 = IGUser.objects.create(
            project=self.project2,
            name='user1',
            createdFromImage=self.image,
            author=self.anne
        )

        UserHashtagUse.objects.create(
            project=self.project2,
            igUser=u_1,
            hashtag=h_1,
            image=self.image,
            author=self.anne
        )

        UserHashtagUse.objects.create(
            project=self.project2,
            igUser=u_1,
            hashtag=h_2,
            image=self.image,
            author=self.anne
        )

        c = Client()
        response = c.get(pre_path + '/b/fx_api/matrix/%s/' % self.project1.pk, headers={
            'Authorization': 'Bearer %s' % self.token
        })

        content = io.BytesIO(b"".join(response.streaming_content))
        wrapper = io.TextIOWrapper(content, encoding='utf-8')

        resulting_csv = wrapper.read()

        assert resulting_csv == "%s%s%s" % (chr(34), chr(34), chr(10))

    def test_matrix_uses_a_fixed_number_of_queries(self):
        from django.http import StreamingHttpResponse
        from functions_api.functions.stream_create_matrix.logic import stream_create_matrix

        hashtags = [Hashtag.objects.create(project=self.project1, content='h%s' % i, createdFromImage=self.image,
                                           author=self.anne) for i in range(20)]
        users = [IGUser.objects.create(project=self.project1, name='u%s' % i, createdFromImage=self.image,
                                       author=self.anne) for i in range(20)]
        for i, hashtag in enumerate(hashtags):
            UserHashtagUse.objects.create(project=self.project1, igUser=users[i], hashtag=hashtag,
                                          image=self.image, author=self.anne)

        # Counts, users and hashtags: three queries whatever the size of the project (not one per pair)
        with self.assertNumQueries(3):
            response = stream_create_matrix(self.project1, StreamingHttpResponse(content_type='text/csv'))
            rows = b"".join(response.streaming_content).decode().splitlines()

        assert len(rows) == 21
        assert rows[0] == ';' + ';'.join('u%s' % i for i in range(20))
        assert rows[5] == 'h4;' + ';'.join('1' if i == 4 else '0' for i in range(20))
