import re
from logging import getLogger

from django.conf import settings
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from .utils import handle_seo_redirects


logger = getLogger(__name__)


class RedirectsMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if not getattr(settings, 'SEO_USE_REDIRECTS', False):
            return

        if request.method == 'GET' and isinstance(exception, Http404):
            handle_seo_redirects(request)
        return
