# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import django
from django.contrib import admin
from tests.userapp.admin import alternative_site
from django.conf.urls import url
from django.urls import include


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^alt-admin/', alternative_site.urls),
    url(r'^', include('tests.userapp.urls')),
]
