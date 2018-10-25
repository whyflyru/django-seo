#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import importlib

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from .utils import create_dynamic_model, register_model_in_admin


RedirectPattern = None
Redirect = None


def setup():
    global RedirectPattern
    global Redirect
    is_loaded = False
    # Look for Metadata subclasses in appname/seo.py files
    for app in settings.INSTALLED_APPS:
        try:
            module_name = '%s.seo' % str(app)
            importlib.import_module(module_name)
            is_loaded = True
        except ImportError:
            pass

    # if SEO_MODELS is defined, create a default Metadata class
    if hasattr(settings, 'SEO_MODELS') and not is_loaded:
        importlib.import_module('djangoseo.default')

    # if SEO_USE_REDIRECTS is enabled, add model for redirect and register it in admin
    if getattr(settings, 'SEO_USE_REDIRECTS', False):
        def magic_str_method(self):
            return self.redirect_path

        class RedirectPatternMeta:
            verbose_name = _('Redirect pattern')
            verbose_name_plural = _('Redirect patterns')

        RedirectPattern = create_dynamic_model('RedirectPattern', **{
            'url_pattern': models.CharField(
                verbose_name=_('URL pattern'),
                max_length=250
            ),
            'site': models.ForeignKey(
                to='sites.Site',
                on_delete=models.CASCADE,
                verbose_name=_('site')
            ),
            'redirect_path':  models.CharField(
                verbose_name=_('redirect path'),
                max_length=250
            ),
            'subdomain': models.CharField(
                verbose_name=_('subdomain'),
                max_length=250,
                blank=True,
                null=True,
                default=''
            ),
            'all_subdomains': models.BooleanField(
                verbose_name=_('all subdomains'),
                default=False,
                help_text=_('Pattern works for all subdomains')
            ),
            '__str__': magic_str_method,
            'Meta': RedirectPatternMeta
        })

        RedirectPatternAdmin = type('RedirectPatternAdmin', (admin.ModelAdmin,), {
            'list_display': ['url_pattern', 'redirect_path', 'site', 'subdomain', 'all_subdomains'],
            'list_display_links': ['url_pattern'],
            'list_filter': ['all_subdomains'],
            'search_fields': ['redirect_path'],
        })

        class RedirectMeta:
            verbose_name = _('redirect')
            verbose_name_plural = _('redirects')
            db_table = 'django_redirect'
            unique_together = (('site', 'old_path'),)
            ordering = ('old_path',)

        def redirect_str_method(self):
            return '%s ---> %s' % (self.old_path, self.new_path)

        from django.contrib.sites.models import Site

        Redirect = create_dynamic_model('RedirectPattern', **{
            'site': models.ForeignKey(
                to=Site,
                on_delete=models.CASCADE,
                verbose_name=_('site')
            ),
            'old_path': models.CharField(
                verbose_name=_('redirect from'),
                max_length=200,
                db_index=True,
                help_text=_("This should be an absolute path, excluding the domain name. Example: '/events/search/'."),
            ),
            'new_path': models.CharField(
                verbose_name=_('redirect to'),
                max_length=200,
                blank=True,
                help_text=_("This can be either an absolute path (as above) or a full URL starting with 'http://'."),
            ),
            'subdomain': models.CharField(
                verbose_name=_('subdomain'),
                max_length=250,
                blank=True,
                null=True,
                default=''
            ),
            'all_subdomains': models.BooleanField(
                verbose_name=_('all subdomains'),
                default=False,
                help_text=_('Pattern works for all subdomains')
            ),
            '__str__': redirect_str_method,
            'Meta': RedirectMeta
        })

        RedirectAdmin = type('RedirectAdmin', (admin.ModelAdmin,), {
            'list_display': ('old_path', 'new_path'),
            'list_filter': ('site',),
            'search_fields': ('old_path', 'new_path'),
            'radio_fields': {'site': admin.VERTICAL}
        })

        register_model_in_admin(RedirectPattern, RedirectPatternAdmin)
        register_model_in_admin(Redirect, RedirectAdmin)

    from djangoseo.base import register_signals
    register_signals()
