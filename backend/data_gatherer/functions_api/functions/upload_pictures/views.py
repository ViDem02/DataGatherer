from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from functions_api.common import LogicApiBaseAPIView
from functions_api.functions.upload_pictures.logic import upload_files
from storage_api.models.project_models import Project
from storage_api.serializers.common_serializers import validate_image_upload


class FileUploadView(LogicApiBaseAPIView):

    def post(self, request):
        project = get_object_or_404(Project, pk=request.data.get('project'), author=request.user)
        files = request.FILES.getlist('files')

        # Validate the whole batch first so a bad file doesn't leave a half-uploaded batch behind
        for file in files:
            validate_image_upload(file)

        upload_files(files, project, request.user)
        return Response("files have been uploaded", status.HTTP_200_OK)
