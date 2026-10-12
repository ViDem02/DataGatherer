import csv

from django.contrib.auth import authenticate
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connections
from django.test import TransactionTestCase
from tqdm import tqdm

from job_api.logic import work_job, calculate_whole_file
from job_api.models import *
from storage_api.models.data_models import *

def close_db_connections(func, *args, **kwargs):
    """
    Decorator to explicitly close db connections during threaded execution

    Note this is necessary to work around:
    https://code.djangoproject.com/ticket/22420
    """

    def _close_db_connections(*args, **kwargs):
        ret = None
        try:
            ret = func(*args, **kwargs)
        finally:
            for conn in connections.all():
                conn.close()
        return ret

    return _close_db_connections


class ModelsTests(TransactionTestCase):
    def setUp(self):

        with tqdm(total=9, desc="setting up job_api test", unit="frame", leave=False) as pbar:
            self.hashtags = []
            self.ig_users = []
            self.hashtag_entities = []

            User.objects.create_user(
                email="test@test.it",
                username='test',
                password='test',
            )

            self.project = Project.objects.create(
                name='Test',
                author=authenticate(
                    username="test",
                    password='test'
                )
            )

            self.create_images()
            pbar.update(1)

            self.usernames = ['Anne', 'Ben', 'Cara', 'Dorian', 'Elena']
            self.hashtags = [
                ['a1', 'a2', 'a3'],
                ['b1'],
                ['c1'],
                ['d1', 'd2'],
                ['e1', 'e2']
            ]

            self.create_users()
            pbar.update(1)

            self.create_hashtags()
            pbar.update(1)

            for i in range(5):
                user = self.ig_users[i]
                for j in range(len(self.hashtags[i])):
                    UserHashtagUse.objects.create(
                        author=authenticate(
                            username="test",
                            password='test'
                        ),
                        project=self.project,
                        igUser=user,
                        hashtag=Hashtag.objects.get(content=self.hashtags[i][j]),
                        image=self.images[i]
                    )
                pbar.update(1)

    @close_db_connections
    def create_images(self):
        from django.conf import settings

        with tqdm(total=5, desc="Creating images", unit="frame", leave=False) as pbar:
            with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
                _file = SimpleUploadedFile('test_screenshot', infile.read())
                self.images = []
                for i in range(5):
                    self.images.append(Image.objects.create(
                        file=_file,
                        userId=i,
                        isDataGathered=False,
                        project=self.project,
                        average_hash=None,
                        isSimilarTo=None,
                        author=authenticate(
                            username="test",
                            password='test'
                        )
                    ))
                    pbar.update(1)

    def create_hashtags(self):
        for i in range(5):
            for hashtag_item in self.hashtags[i]:
                self.hashtag_entities.append(Hashtag.objects.create(
                    author=authenticate(
                        username="test",
                        password='test'
                    ),
                    project=self.project,
                    content=hashtag_item,
                    createdFromImage=self.images[i]
                ))

    def create_users(self):
        for i in range(5):
            self.ig_users.append(IGUser.objects.create(
                author=authenticate(
                    username="test",
                    password='test'
                ),
                project=self.project,
                name=self.usernames[i],
                createdFromImage=self.images[i]
            ))

    def test_project_is_initiated_correctly(self):
        job = Job.objects.create(
            title="test",
            taskGranularity=5,
            project=self.project
        )
        initiate_job(job)
        assert job.isInitiated

        for i in range(5):
            JobIGUser.objects.get(name=self.usernames[i])

        for i in range(5):
            for j in range(len(self.hashtags[i])):
                print(self.hashtags[i][j])
                JobHashtag.objects.get(content=self.hashtags[i][j])

        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="a1"),
            user=JobIGUser.objects.get(name="Anne"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="a2"),
            user=JobIGUser.objects.get(name="Anne"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="a3"),
            user=JobIGUser.objects.get(name="Anne"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="b1"),
            user=JobIGUser.objects.get(name="Ben"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="c1"),
            user=JobIGUser.objects.get(name="Cara"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="d1"),
            user=JobIGUser.objects.get(name="Dorian"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="d2"),
            user=JobIGUser.objects.get(name="Dorian"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="e1"),
            user=JobIGUser.objects.get(name="Elena"),
        )
        JobUserHashtagUse.objects.get(
            hashtag=JobHashtag.objects.get(content="e2"),
            user=JobIGUser.objects.get(name="Elena"),
        )

        assert JobUserHashtagUse.objects.all().count() == 9

    @close_db_connections
    def test_job_creates_correct_whole_file(self):
        from django.conf import settings

        with open(settings.TEST_MEDIA_ROOT + '/test_screenshot.png', 'rb') as infile:
            _file = SimpleUploadedFile('test_screenshot', infile.read())
            self.images.append(Image.objects.create(
                file=_file,
                userId=6,
                isDataGathered=False,
                project=self.project,
                average_hash=None,
                isSimilarTo=None,
                author=authenticate(
                    username="test",
                    password='test'
                )
            ))

        UserHashtagUse.objects.create(
            author=authenticate(
                username="test",
                password='test'
            ),
            project=self.project,
            igUser=self.ig_users[0],
            hashtag=Hashtag.objects.get(content='a1'),
            image=self.images[5]
        )

        self.hashtags.append(Hashtag.objects.create(
            author=authenticate(
                username="test",
                password='test'
            ),
            project=self.project,
            content='z1',
            createdFromImage=self.images[0]
        ))

        UserHashtagUse.objects.create(
            author=authenticate(
                username="test",
                password='test'
            ),
            project=self.project,
            igUser=self.ig_users[0],
            hashtag=Hashtag.objects.get(content='z1'),
            image=self.images[0]
        )

        UserHashtagUse.objects.create(
            author=authenticate(
                username="test",
                password='test'
            ),
            project=self.project,
            igUser=self.ig_users[3],
            hashtag=Hashtag.objects.get(content='z1'),
            image=self.images[3]
        )

        job = Job.objects.create(
            title="test",
            taskGranularity=5,
            project=self.project
        )
        initiate_job(job)
        work_job(job, wait=True)
        calculate_whole_file(job)

        expectation = [
            [""] + self.usernames,
            ['a1', '2', '0', '0', '0', '0'],
            ['a2', '1', '0', '0', '0', '0'],
            ['a3', '1', '0', '0', '0', '0'],
            ['b1', '0', '1', '0', '0', '0'],
            ['c1', '0', '0', '1', '0', '0'],
            ['d1', '0', '0', '0', '1', '0'],
            ['d2', '0', '0', '0', '1', '0'],
            ['e1', '0', '0', '0', '0', '1'],
            ['e2', '0', '0', '0', '0', '1'],
            ['z1', '1', '0', '0', '1', '0'],
        ]


        lines = 0
        data = []
        with open(job.file.path, "r") as file:
            csv_reader = csv.reader(file, delimiter=";", quoting=csv.QUOTE_ALL)
            for line in csv_reader:
                data.append(line)
                lines = lines + 1

        for i in range(lines):
            assert all(x == y for x, y in zip(data[i], expectation[i]))

    @close_db_connections
    def test_job_is_not_completed_when_a_task_fails(self):
        import threading
        from unittest import mock

        job = Job.objects.create(
            title="failing",
            taskGranularity=5,
            project=self.project
        )
        initiate_job(job)
        assert Task.objects.filter(job=job).count() == 2

        # The first task to write its file fails; the other one succeeds
        real_writer = csv.writer
        lock = threading.Lock()
        calls = []

        def flaky_writer(*args, **kwargs):
            with lock:
                calls.append(1)
                first = len(calls) == 1
            if first:
                raise RuntimeError("simulated failure")
            return real_writer(*args, **kwargs)

        with mock.patch('job_api.logic.csv.writer', side_effect=flaky_writer):
            work_job(job, wait=True)

        job.refresh_from_db()
        assert job.isCompleted is False
        assert job.isWorking is False
        assert Task.objects.filter(job=job, isCompleted=True).count() == 1
        assert Task.objects.filter(job=job, inProgress=True).count() == 0

        # Working the job again only redoes the failed task, then the job is complete
        work_job(job, wait=True)
        job.refresh_from_db()
        assert job.isCompleted is True
        assert Task.objects.filter(job=job, isCompleted=False).count() == 0
