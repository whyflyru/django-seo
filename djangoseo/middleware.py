import re
from django.conf import settings

from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404

from .models import RedirectPattern


class RedirectsMiddleware(object):

    def process_exception(self, request, exception):
        if not getattr(settings, 'SEO_USE_REDIRECTS', False):
            return

        if request.method == 'GET' and isinstance(exception, Http404):
            full_path = request.get_full_path()
            current_site = get_current_site(request)
            subdomain = getattr(request, 'subdomain', '')

            redirect_patterns = RedirectPattern.objects.filter(site=current_site, subdomain=subdomain)

            for redirect_pattern in redirect_patterns:
                if re.match(redirect_pattern.url_pattern, full_path):
                    Redirect.objects.get_or_create(
                        site=current_site,
                        old_path=full_path,
                        new_path=redirect_pattern.redirect_path
                    )
        return
