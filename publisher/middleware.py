from django.utils import timezone
from django.conf import settings
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import unquote

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname_raw = request.COOKIES.get('user_timezone')
        tzname = unquote(tzname_raw) if tzname_raw else settings.TIME_ZONE
        try:
            tz = ZoneInfo(tzname)
        except ZoneInfoNotFoundError:
            tz = ZoneInfo(settings.TIME_ZONE)
        with timezone.override(tz):
            return self.get_response(request)