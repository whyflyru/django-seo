#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import importlib

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .utils import create_dynamic_model, register_model_in_admin


RedirectPattern = None


def setup():
    global RedirectPattern
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

        class Meta:
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
            'Meta': Meta
        })

        register_model_in_admin(RedirectPattern)

    from djangoseo.base import register_signals
    register_signals()
