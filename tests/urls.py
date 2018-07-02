# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.urls import patterns, include
from django.contrib import admin
from userapp.admin import alternative_site


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^alt-admin/', include(alternative_site.urls)),
    url(r'^', include('userapp.urls')),
)
