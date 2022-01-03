from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
import re


class RequireAccessMiddleware(object):
    """
    Middleware component that wraps the
    matching URL patterns. To use, add the class to MIDDLEWARE_CLASSES and 
    define ACCESS_REQUIRED_URLS and ACCESS_REQUIRED_URLS_EXCEPTIONS in
    settings.py. For example:
    ------
    ACCESS_REQUIRED_URLS = (
        r'/topsecret/(.*)$',
    )
    ACCESS_REQUIRED_URLS_EXCEPTIONS = (
        r'/topsecret/login(.*)$', 
        r'/topsecret/logout(.*)$',
    )
    -----
    LOGIN_REQUIRED_URLS is where you define URL patterns; each pattern must 
    be a valid regex.

    LOGIN_REQUIRED_URLS_EXCEPTIONS is, conversely, where you explicitly 
    define any exceptions (like login and logout URLs).

    If no matches are found, nothing is done.
    """
    def __init__(self, get_response):
        self.required = tuple([re.compile(url) for url in settings.ACCESS_REQUIRED_URLS])
        self.exceptions = tuple([re.compile(url) for url in settings.ACCESS_REQUIRED_URLS_EXCEPTIONS])
        self.get_response = get_response

    def __call__(self, request):
        if any([url.match(request.path) for url in self.required]):

            if any([url.match(request.path) for url in self.exceptions]):
                return self.get_response(request)

            elif request.user.is_authenticated and \
                 len(request.user.userinfo.user_site_access()):
                return self.get_response(request)

            else:
                return redirect_to_login(request.get_full_path(), settings.LOGIN_URL, REDIRECT_FIELD_NAME)

        else:
            return self.get_response(request)
