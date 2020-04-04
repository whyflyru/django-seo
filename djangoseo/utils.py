# -*- coding: utf-8 -*-
import logging
import re
import importlib

import django
import six
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.module_loading import import_string
from django.utils.html import conditional_escape
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import (URLResolver as RegexURLResolver, URLPattern as RegexURLPattern, Resolver404, get_resolver,
                         clear_url_caches)

logger = logging.getLogger(__name__)


class NotSet(object):
    """ A singleton to identify unset values (where None would have meaning) """

    def __str__(self):
        return "NotSet"

    def __repr__(self):
        return self.__str__()


NotSet = NotSet()


class Literal(object):
    """ Wrap literal values so that the system knows to treat them that way """

    def __init__(self, value):
        self.value = value


def _pattern_resolve_to_name(pattern, path):
    if django.VERSION < (2, 0):
        match = pattern.regex.search(path)
    else:
        match = pattern.pattern.regex.search(path)
    if match:
        name = ""
        if pattern.name:
            name = pattern.name
        elif hasattr(pattern, '_callback_str'):
            name = pattern._callback_str
        else:
            name = "%s.%s" % (pattern.callback.__module__, pattern.callback.func_name)
        return name


def _resolver_resolve_to_name(resolver, path):
    tried = []
    django1 = django.VERSION < (2, 0)
    if django1:
        match = resolver.regex.search(path)
    else:
        match = resolver.pattern.regex.search(path)
    if match:
        new_path = path[match.end():]
        for pattern in resolver.url_patterns:
            try:
                if isinstance(pattern, RegexURLPattern):
                    name = _pattern_resolve_to_name(pattern, new_path)
                elif isinstance(pattern, RegexURLResolver):
                    name = _resolver_resolve_to_name(pattern, new_path)
            except Resolver404 as e:
                if django1:
                    tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
                else:
                    tried.extend([(pattern.pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
            else:
                if name:
                    return name
                if django1:
                    tried.append(pattern.regex.pattern)
                else:
                    tried.append(pattern.pattern.regex.pattern)
        raise Resolver404({'tried': tried, 'path': new_path})


def resolve_to_name(path, urlconf=None):
    try:
        return _resolver_resolve_to_name(get_resolver(urlconf), path)
    except Resolver404:
        return None


def _replace_quot(match):
    unescape = lambda v: v.replace('&quot;', '"').replace('&amp;', '&')
    return u'<%s%s>' % (unescape(match.group(1)), unescape(match.group(3)))


def escape_tags(value, valid_tags):
    """ Strips text from the given html string, leaving only tags.
        This functionality requires BeautifulSoup, nothing will be
        done otherwise.
        This isn't perfect. Someone could put javascript in here:
              <a onClick="alert('hi');">test</a>
            So if you use valid_tags, you still need to trust your data entry.
            Or we could try:
              - only escape the non matching bits
              - use BeautifulSoup to understand the elements, escape everything
                else and remove potentially harmful attributes (onClick).
              - Remove this feature entirely. Half-escaping things securely is
                very difficult, developers should not be lured into a false
                sense of security.
    """
    # 1. escape everything
    value = conditional_escape(value)

    # 2. Reenable certain tags
    if valid_tags:
        # TODO: precompile somewhere once?
        tag_re = re.compile(r'&lt;(\s*/?\s*(%s))(.*?\s*)&gt;' %
                            u'|'.join(re.escape(tag) for tag in valid_tags))
        value = tag_re.sub(_replace_quot, value)

    # Allow comments to be hidden
    value = value.replace("&lt;!--", "<!--").replace("--&gt;", "-->")

    return mark_safe(value)


def _get_seo_content_types(seo_models):
    """ Returns a list of content types from the models defined in settings
    (SEO_MODELS)
    """
    from django.contrib.contenttypes.models import ContentType
    try:
        return [ContentType.objects.get_for_model(m).id for m in seo_models]
    except:  # previously caught DatabaseError
        # Return an empty list if this is called too early
        return []


def get_seo_content_types(seo_models):
    return lazy(_get_seo_content_types, list)(seo_models)


def _reload_urlconf():
    """
    Reload Django URL configuration and clean caches
    """
    module = importlib.import_module(settings.ROOT_URLCONF)
    if six.PY2:
        reload(module)
    else:
        importlib.reload(module)
    clear_url_caches()


def register_model_in_admin(model, admin_class=None):
    """
    Register model in Django admin interface
    """
    from django.contrib import admin
    admin.site.register(model, admin_class)

    _reload_urlconf()


def create_dynamic_model(model_name, app_label='djangoseo', **attrs):
    """
    Create dynamic Django model
    """
    module_name = '%s.models' % app_label
    default_attrs = {
        '__module__': module_name,
        '__dynamic__': True
    }
    attrs.update(default_attrs)
    if six.PY2:
        model_name = str(model_name)
    return type(model_name, (models.Model,), attrs)


def import_tracked_models():
    """
    Import models
    """
    redirects_models = getattr(settings, 'SEO_TRACKED_MODELS', [])
    models = []
    for model_path in redirects_models:
        try:
            model = import_string(model_path)
            models.append(model)
        except ImportError as e:
            logging.warning("Failed to import model from path '%s'" % model_path)
    return models


def handle_seo_redirects(request):
    """
    Handle SEO redirects. Create Redirect instance if exists redirect pattern.
    :param request: Django request
    """
    from .models import RedirectPattern, Redirect

    if not getattr(settings, 'SEO_USE_REDIRECTS', False):
        return

    full_path = request.get_full_path()
    current_site = get_current_site(request)
    subdomain = getattr(request, 'subdomain', '')

    redirect_patterns = RedirectPattern.objects.filter(
        Q(site=current_site),
        Q(subdomain=subdomain) | Q(all_subdomains=True)
    ).order_by('all_subdomains')

    for redirect_pattern in redirect_patterns:
        if re.match(redirect_pattern.url_pattern, full_path):
            kwargs = {
                'site': current_site,
                'old_path': full_path,
                'new_path': redirect_pattern.redirect_path,
                'subdomain': redirect_pattern.subdomain,
                'all_subdomains': redirect_pattern.all_subdomains
            }
            try:
                Redirect.objects.get_or_create(**kwargs)
            except Exception:
                logger.warning('Failed to create redirection', exc_info=True, extra=kwargs)
            break
