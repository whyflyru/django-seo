import re
from logging import getLogger

from django.conf import settings
from django.http import Http404

from .utils import handle_seo_redirects


logger = getLogger(__name__)


# TODO: replace after upgrade to Django 1.10
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

        if request.method == 'GET' and isinstance(exception, Http404):
            handle_seo_redirects(request)
        return
