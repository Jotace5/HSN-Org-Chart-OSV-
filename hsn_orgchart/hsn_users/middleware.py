from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import Group

class CustomSessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Viewer').exists():
                # Set a shorter session expiry for viewers (e.g., 30 minutes)
                request.session.set_expiry(timedelta(minutes=30))
            else:
                # Set a longer session expiry for admins (e.g., 1 hour)
                request.session.set_expiry(timedelta(hours=1))

        response = self.get_response(request)
        return response
