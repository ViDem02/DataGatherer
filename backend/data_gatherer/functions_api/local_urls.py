from django.urls import path

from functions_api.functions.compute_index.views import ComputeIndex
from functions_api.functions.extend_network_from_image.views import ExtendNetworkFromImageView
from functions_api.functions.stream_create_matrix.views import StreamCreateMatrixViewSet
from functions_api.functions.upload_pictures import fx_urls as upload_pics_urls
from functions_api.functions.use_default_crop.views import UseDefaultCropView
from django.urls import path, include


urlpatterns = [
    path('up/', include(upload_pics_urls)),
    path('default_crop/', UseDefaultCropView.as_view(), name='use_default_crop_view'),
    path('extend/', ExtendNetworkFromImageView.as_view(), name='extend_network_from_img'),
    path('matrix/<pk>/', StreamCreateMatrixViewSet.as_view(), name='create_matrix'),
    path('compute_index/', ComputeIndex.as_view(), name='compute_index'),
]