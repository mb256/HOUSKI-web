from django.shortcuts import redirect
from django.urls import reverse


EXEMPT_URLS = [
    '/login/',
    '/logout/',
    '/password-change/',
    '/password-change/done/',
    '/admin/',
    '/static/',
    '/media/',
]


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and \
           getattr(request.user, 'must_change_password', False) and \
           not any(request.path.startswith(url) for url in EXEMPT_URLS):
            return redirect(reverse('password_change'))
        return self.get_response(request)
