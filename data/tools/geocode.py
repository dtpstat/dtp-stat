import herepy
import requests
import logging
from django.conf import settings

log = logging.getLogger(__name__)


def geocoder_yandex(address, kind=None):
    params = {
        "geocode": address,
        "apikey": settings.YANDEX_TOKEN,
        "format": "json"
    }
    if kind is not None:
        params['kind'] = kind

    url = "https://geocode-maps.yandex.ru/1.x"
    r = requests.get(url, params=params)

    data = {}

    try:
        json = r.json()
        if not json['response']['GeoObjectCollection']['featureMember']:
            log.error('geocoder_yandex result is empty')
            return None
        geo = json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

        data['lat'] = float(geo['Point']['pos'].split(" ")[1])
        data['long'] = float(geo['Point']['pos'].split(" ")[0])

        data['address'] = geo['metaDataProperty']['GeocoderMetaData']['text']

        address_components_street = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                                     x['kind'] == "street"]
        if address_components_street:
            data['street'] = address_components_street[0]['name']


        parent_region_data = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                              x['kind'] == "province"]
        if len(parent_region_data) > 1:
            data['parent_region'] = parent_region_data[1]['name']

        data['components'] = [x['name'] for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                           x['kind'] in ["locality", "area"]]

        if "Россия" in data['address']:
            region_data = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                           (x['kind'] in ["locality"] and x['name'] != data['parent_region'])]
            if region_data:
                data['region'] = region_data[0]['name']
            else:
                region_data = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                               (x['kind'] in ["area"] and x['name'] != data['parent_region'])]
                if region_data:
                    data['region'] = region_data[0]['name']

    except Exception as e:
        log.error('geocoder_yandex error: %s', e)

    return data if data != {} else None


def geocoder_here(address=None, coords=None):
    api_key = settings.HERE_TOKEN
    response = None

    if address:
        geocoderApi = herepy.GeocoderApi(api_key)
        response = geocoderApi.free_form(address).as_dict()
    elif coords:
        geocoderReverseApi = herepy.GeocoderReverseApi(api_key)
        response = geocoderReverseApi.retrieve_addresses(coords).as_dict()

    if response:
        return {
            'lat': response['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Latitude'],
            "long": response['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Longitude']
        }
    else:
        return None


def geocode(dtp):
    data = geocoder_yandex(dtp.full_address())
    if data:
        here_data = geocoder_here(coords=[data['lat'], data['long']])
        if here_data:
            data['lat'] = here_data['lat']
            data['long'] = here_data['long']
    return data
