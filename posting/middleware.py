from django.utils import timezone
import pytz

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get('user_timezone', 'UTC')
        if tzname in pytz.all_timezones:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.activate(pytz.UTC)
        response = self.get_response(request)
        return response