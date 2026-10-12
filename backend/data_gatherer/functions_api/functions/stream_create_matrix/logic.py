import csv

from django.db.models import Count
from django.http import StreamingHttpResponse

from storage_api.models.data_models import Hashtag, IGUser, UserHashtagUse
from storage_api.models.project_models import Project


class CSVBuffer:
    def write(self, value):
        return value


def stream_create_matrix(project: Project, response: StreamingHttpResponse):
    # Three queries whatever the size of the project: the database counts the uses of every
    # user-hashtag pair in one GROUP BY, instead of one COUNT query per pair.
    counts = {
        (row['hashtag_id'], row['igUser_id']): row['uses']
        for row in UserHashtagUse.objects.filter(project=project)
        .values('hashtag_id', 'igUser_id')
        .annotate(uses=Count('id'))
    }

    # Only the users and hashtags used at least once appear in the matrix
    prj_users = list(
        IGUser.objects.filter(project=project, userhashtaguse__isnull=False).distinct().order_by('pk')
    )
    prj_hashtags = Hashtag.objects.filter(
        project=project, userhashtaguse__isnull=False
    ).distinct().order_by('pk')

    writer = csv.writer(CSVBuffer(), delimiter=';')

    def rows():
        yield writer.writerow([''] + [user.matrix_name for user in prj_users])
        for hashtag in prj_hashtags.iterator():
            yield writer.writerow(
                [hashtag.content] + [counts.get((hashtag.pk, user.pk), 0) for user in prj_users]
            )

    response.streaming_content = rows()
    return response
