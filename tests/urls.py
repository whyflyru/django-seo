# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.urls import include
from django.contrib import admin
from userapp.admin import alternative_site


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^alt-admin/', alternative_site.urls),
    url(r'^', include('userapp.urls')),
]
