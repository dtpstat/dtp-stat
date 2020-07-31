import requests
import calendar
import datetime


def get_donate_data(request):
    donate_data_r = requests.get(
        'https://donate.city4people.ru/ajax/ajax_public.php?context=get__donationsInfo33&domain=beta.dtp-stat.ru'
    )

    try:
        donate_data = donate_data_r.json()
        donate_data['progress'] = donate_data['paymentsInfo']['sum_total']*100/donate_data['paymentsInfo']['sum_goal']
        donate_data['days_left'] = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1] + 1 - datetime.datetime.now().day
    except:
        donate_data = None

    return {'donate_data':donate_data}