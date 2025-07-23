import datetime
from django.conf import settings as django_settings
from constance import config


def get_donate_data(request):
    sum_total = config.DONATE_SUM_TOTAL
    sum_goal = config.DONATE_SUM_GOAL
    end_date_str = config.DONATE_END_DATE

    try:
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        now = datetime.datetime.now()
        days_left = (end_date - now).days
    except (ValueError, TypeError):
        days_left = 0

    if sum_goal > 0:
        progress = (sum_total * 100) / sum_goal
    else:
        progress = 0

    donate_data = {
        'paymentsInfo': {
            'sum_total': sum_total,
            'sum_goal': sum_goal,
        },
        'progress': progress,
        'days_left': days_left,
    }

    return {'donate_data': donate_data}


def settings(request):
    return {
        'settings': django_settings,
    }
