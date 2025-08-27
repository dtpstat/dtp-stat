from django.utils import timezone
from django.conf import settings
import pytz
from pytz import UnknownTimeZoneErro

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get('user_timezone', settings.TIME_ZONE)
        try:
            tz = ZoneInfo(tzname)
        except Exception:
            tz = ZoneInfo(settings.TIME_ZONE)
        timezone.activate(tz)
        response = self.get_response(request)
        return response