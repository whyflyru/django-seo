import re
from logging import getLogger

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.http import Http404

from .models import RedirectPattern


logger = getLogger(__name__)


class RedirectsMiddleware(object):

    def process_exception(self, request, exception):
        if not getattr(settings, 'SEO_USE_REDIRECTS', False):
            return

        if request.method == 'GET' and isinstance(exception, Http404):
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
                        'new_path': redirect_pattern.redirect_path
                    }
                    try:
                        Redirect.objects.get_or_create(**kwargs)
                    except Exception:
                        logger.warning('Failed to create redirection', exc_info=True, extra=kwargs)
                    break
        return
