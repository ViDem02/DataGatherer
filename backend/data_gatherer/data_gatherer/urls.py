"""
URL configuration for data_gatherer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from data_gatherer.admin_sites import global_admin_site
from functions_api import local_urls as fx_urls
from storage_api import local_urls as storage_urls
from storage_api.admin import admin
import re

from django.urls import path, include, re_path
from django.conf import settings
from rest_framework_simplejwt.views import TokenVerifyView

from data_gatherer.auth_views import CookieTokenObtainView, CookieTokenRefreshView, LogoutView
from storage_api.views.media_views import ProtectedMediaView


pre_path = settings.PRE_PATH


token_urlpatterns = [
    path('obtain/', CookieTokenObtainView.as_view(), name='token_obtain_pair'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='token_logout'),
]

public_paths = [
    path('admin/', global_admin_site.urls),
    path('token/', include(token_urlpatterns)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

private_paths = [
    path('fx_api/', include(fx_urls)),
    path('storage_api/', include(storage_urls)),
]

urlpatterns = [
    path('a/', include(public_paths)),
    path('b/', include(private_paths)),
]

urlpatterns = [
    path(pre_path, include(urlpatterns)),
    # Uploaded files are only served to logged-in owners, at the URL their FileField reports
    re_path(r'^%s(?P<file_path>.+)$' % re.escape(settings.MEDIA_URL.lstrip('/')),
            ProtectedMediaView.as_view(), name='protected_media'),
]
