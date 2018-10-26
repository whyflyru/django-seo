from logging import getLogger

from django import http
from django.apps import apps
from django.db.models import Q
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured

from .models import Redirect
from .utils import handle_seo_redirects


logger = getLogger(__name__)


# TODO: replace after removing support for old versions of Django
class MiddlewareMixin(object):
    """
    This mixin a full copy of Django 1.10 django.utils.deprecation.MiddlewareMixin.
    Needed for compatibility reasons.
    """
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class RedirectsMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if not getattr(settings, 'SEO_USE_REDIRECTS', False):
            return

        if request.method == 'GET' and isinstance(exception, http.Http404):
            handle_seo_redirects(request)
        return


class RedirectFallbackMiddleware(MiddlewareMixin):
    # Defined as class-level attributes to be subclassing-friendly.
    response_gone_class = http.HttpResponseGone
    response_redirect_class = http.HttpResponsePermanentRedirect

    def __init__(self, get_response=None):
        if not apps.is_installed('django.contrib.sites'):
            raise ImproperlyConfigured(
                'You cannot use RedirectFallbackMiddleware when '
                'django.contrib.sites is not installed.'
            )
        super(RedirectFallbackMiddleware, self).__init__(get_response)

    def process_response(self, request, response):
        # No need to check for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        subdomain = getattr(request, 'subdomain', '')
        full_path = request.get_full_path()
        current_site = get_current_site(request)

        redirect = Redirect.objects.filter(
            Q(site=current_site),
            Q(old_path=full_path),
            Q(subdomain=subdomain) | Q(all_subdomains=True)
        ).order_by('all_subdomains').first()

        if redirect is None and settings.APPEND_SLASH and not request.path.endswith('/'):
            redirect = Redirect.objects.filter(
                Q(site=current_site),
                Q(old_path=request.get_full_path(force_append_slash=True)),
                Q(subdomain=subdomain) | Q(all_subdomains=True)
            ).order_by('all_subdomains').first()
        if redirect is not None:
            if redirect.new_path == '':
                return self.response_gone_class()
            return self.response_redirect_class(redirect.new_path)

        # No redirect was found. Return the response.
        return response
