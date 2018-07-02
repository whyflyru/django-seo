# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url


urlpatterns = [
    url(r'^pages/([\w\d-]+)/', 'userapp.views.page_detail', name="userapp_page_detail"),
    url(r'^products/(\d+)/', 'userapp.views.product_detail', name="userapp_product_detail"),
    url(r'^tags/(.+)/', 'userapp.views.tag_detail', name="userapp_tag"),
    url(r'^my/view/(.+)/', 'userapp.views.my_view', name="userapp_my_view"),
    url(r'^my/other/view/(.+)/', 'userapp.views.my_other_view', name="userapp_my_other_view"),
]
