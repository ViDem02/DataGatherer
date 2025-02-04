from django.urls import path, include
from rest_framework import routers
from .admin import admin
from storage_api.views.data_views import *
from storage_api.views.project_views import *
from storage_api.views.image_views import *

imageRouter = routers.DefaultRouter()
imageRouter.register(r'', ImageViewSet)

imgDataRouter = routers.DefaultRouter()
imgDataRouter.register(r'', ImgDataViewSet)

imgCropRouter = routers.DefaultRouter()
imgCropRouter.register(r'', ImgCropViewSet)

projectRouter = routers.DefaultRouter()
projectRouter.register(r'', ProjectViewSet)

hashtagRouter = routers.DefaultRouter()
hashtagRouter.register(r'', HashtagViewSet)

igUserRouter = routers.DefaultRouter()
igUserRouter.register(r'', IGUserViewSet)

userHashtagUseRouter = routers.DefaultRouter()
userHashtagUseRouter.register(r'', UserHashtagUseViewSet)

projectDefaultCropRouter = routers.DefaultRouter()
projectDefaultCropRouter.register(r'', ProjectDefaultCropViewSet)


urlpatterns = [
    path('images/', include(imageRouter.urls)),
    path('img_data/', include(imgDataRouter.urls)),
    path('img_crops/', include(imgCropRouter.urls)),
    path('projects/', include(projectRouter.urls)),
    path('hashtags/', include(hashtagRouter.urls)),
    path('ig_users/', include(igUserRouter.urls)),
    path('user_hashtag_uses/', include(userHashtagUseRouter.urls)),
    path('prj_default_crop/', include(projectDefaultCropRouter.urls))
]