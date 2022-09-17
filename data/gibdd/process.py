import datetime
import re

import pytz
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.utils import timezone

from data import models
from data.gibdd.conf import log


def add_dtp_record(item):
    tag_code = item.get("tag_code")
    area_code = item.get("area_code")
    parent_code = item.get("parent_code")
    item = {key: item[key] for key in item if key not in ['tag_code', 'area_code', 'parent_code']}

    dtp = models.DTP.objects.get_or_create(gibdd_slug=item['KartId'])[0]

    if area_code and parent_code:
        dtp.region = get_object_or_404(models.Region, gibdd_code=area_code, parent_region__gibdd_code=parent_code)

    if not dtp.region:
        log.warn('Регион не найден для ДТП %s' % item['KartId'])


    dtp.gibdd_latest_check = timezone.now()

    tag = get_object_or_404(models.Tag, code=tag_code)
    dtp.tags.add(tag)

    dtp.save()

    if dtp.only_manual_edit or (dtp.region and dtp.data and dtp.data.get('source') and dtp.data.get('source') == item):
        return
    else:
        dtp.gibdd_latest_change = timezone.now()
        dtp.data['source'] = item

        _process_main_data(item, dtp)
        _process_geo_data(item, dtp)
        _add_participants_records(item, dtp)
        _add_related_data(item, dtp)
        _add_extra_filters(item, dtp)

        dtp.save()


def _process_main_data(item, dtp):

    # Цифры по пострадавшим
    dtp.participants = item['K_UCH']
    dtp.injured = item['RAN']
    dtp.dead = item['POG']

    # Дата
    dtp.datetime = pytz.timezone('UTC').localize(
        datetime.datetime.strptime(item['date'] + " " + item['Time'], '%d.%m.%Y %H:%M'))


    dtp.category, created = models.Category.objects.get_or_create(name=item['DTP_V']) if item['DTP_V'] else None
    dtp.light, created = models.Light.objects.get_or_create(name=item['infoDtp']['osv']) if item['infoDtp'][
        'osv'] else None

    dtp.scheme = item['infoDtp']['s_dtp'] if item['infoDtp']['s_dtp'] not in ["290", "390", "490", "590", "690", "790",
                                                                              "890", "990"] else None


def _process_geo_data(item, dtp):
    try:
        lat, long = float(item['infoDtp']['COORD_L']), float(item['infoDtp']['COORD_W'])
    except:
        lat, long = None, None

    address_components = [
        item['infoDtp']['n_p'],
        item['infoDtp']['street'],
        item['infoDtp']['house']
    ]

    road_components = [
        item['infoDtp']['n_p'],
        item['infoDtp']['dor']
    ]
    if item['infoDtp']['km']:
        road_components.append(item['infoDtp']['km'] + " " + "км")

    if address_components[1]:
        street = address_components[1]
        address = ", ".join([x for x in address_components if x]).strip()
    elif road_components[1]:
        street = road_components[1]
        address = ", ".join([x for x in road_components if x]).strip()
    else:
        street = None
        address = None

    if address:
        dtp.address = address

    if street:
        dtp.street = street

    if item['infoDtp']['k_ul']:
        dtp.street_category = item['infoDtp']['k_ul']

    if item['infoDtp']['dor_z'] and item['infoDtp']['dor_z'] != "Не указано":
        dtp.road_category = item['infoDtp']['dor_z']

    if lat and long:
        if not dtp.point_is_verified:
            dtp.point = Point(lat, long)


def _add_participant_record(participant, dtp, vehicle=None):
    # тяжесть
    participant_severity = None
    for severity in models.Severity.objects.all():
        if participant['S_T'] and any(x in participant['S_T'].lower() for x in severity.keywords):
            participant_severity = severity
            break

    try:
        alco = int(participant['ALCO'])
        if not alco:
            alco = None
    except:
        alco = None

    participant_item = models.Participant(
        role=participant['K_UCH'] or None,
        driving_experience=participant['V_ST'] if participant['V_ST'] and int(participant['V_ST']) and int(
            participant['V_ST']) < 90 else None,
        health_status=participant['S_T'] or None,
        gender=participant['POL'] if participant['POL'] and participant['POL'] != "Не определен" else None,
        dtp=dtp,
        vehicle=vehicle,
        severity=participant_severity,
        gibdd_slug=participant['N_UCH'],
        alco=alco,
        absconded=participant['S_SM']
    )
    participant_item.save()

    for violation_item in participant['NPDD']:
        if violation_item != "Нет нарушений":
            violation, created = models.Violation.objects.get_or_create(
                name=violation_item
            )
            if not violation.gibdd_category:
                violation.gibdd_category = 'Основные нарушения'
                violation.save()
            participant_item.violations.add(violation)

    for violation_item in participant['SOP_NPDD']:
        if violation_item != "Нет нарушений":
            violation, created = models.Violation.objects.get_or_create(
                name=violation_item
            )
            if not violation.gibdd_category:
                violation.gibdd_category = 'Сопутствующие нарушения'
                violation.save()
            participant_item.violations.add(violation)


def _add_participants_records(item, dtp):
    models.Vehicle.objects.filter(participant__dtp=dtp).delete()
    dtp.participant_set.all().delete()

    for vehicle_item in item['infoDtp']['ts_info']:
        if vehicle_item.get('t_ts'):
            category, created = models.VehicleCategory.objects.get_or_create(
                name=vehicle_item['t_ts']
            )

            vehicle = models.Vehicle(
                gibdd_slug=vehicle_item['n_ts'],
                year=vehicle_item['g_v'] or None,
                brand=vehicle_item['marka_ts'] or None,
                vehicle_model=vehicle_item['m_ts'] or None,
                color=vehicle_item['color'] or None,
                category=category,
                drive=vehicle_item['r_rul'] or None,
                absconded=vehicle_item['ts_s'] or None,
                ownership_category=vehicle_item['f_sob'] or None,
                ownership=vehicle_item['o_pf'] or None,
            )
            vehicle.save()

            for damage in vehicle_item['m_pov'].split("|"):
                if damage:
                    damage_item, created = models.VehicleDamage.objects.get_or_create(
                        name=damage.strip()
                    )
                    vehicle.damages.add(damage_item)

            for malfunction in vehicle_item['t_n'].split("|"):
                if malfunction and malfunction != "Технические неисправности отсутствуют":
                    damage_item, created = models.VehicleMalfunction.objects.get_or_create(
                        name=malfunction.strip()
                    )
                    vehicle.malfunctions.add(damage_item)

            for participant in vehicle_item['ts_uch']:
                _add_participant_record(participant, dtp, vehicle=vehicle)

    for participant in item['infoDtp']['uchInfo']:
        _add_participant_record(participant, dtp)


def _add_related_data(item, dtp):
    related_data = [
        {
            "model": models.Nearby,
            "dtp_model": dtp.nearby,
            "data": item['infoDtp']['OBJ_DTP'] + item['infoDtp']['sdor'],
            "exclude": [
                'нет объектов',
                "отсутствие",
                'иное место'
            ]
        },
        {
            "model": models.Weather,
            "dtp_model": dtp.weather,
            "data": item['infoDtp']['s_pog'],
            "exclude": []
        },
        {
            "model": models.RoadCondition,
            "dtp_model": dtp.road_conditions,
            "data": item['infoDtp']['ndu'] + [item['infoDtp']['s_pch']],
            "exclude": [
                "не установлены",
            ]
        }
    ]

    for data_item in related_data:
        data_item['dtp_model'].clear()
        data_list = []

        for data_object in data_item['data']:
            if not any(re.search(x, data_object, re.IGNORECASE) for x in data_item['exclude']):
                new_item, created = data_item['model'].objects.get_or_create(
                    name=data_object
                )
                data_list.append(new_item)

        data_item['dtp_model'].add(*data_list)


def _add_extra_filters(item, dtp):
    # severity

    if dtp.dead:
        dtp.severity = get_object_or_404(models.Severity, level=4)
    else:
        severity_levels = [x.severity.level for x in dtp.participant_set.all() if x.severity and x.severity.level]
        if severity_levels:
            dtp.severity = get_object_or_404(models.Severity, level=max(severity_levels))
        else:
            dtp.severity = get_object_or_404(models.Severity, level=1)

    # participatn categories
    dtp.participant_categories.clear()
    participant_categories = {x.slug: x.id for x in models.ParticipantCategory.objects.all()}

    dtp_participants = dtp.participant_set.all()
    dtp_participants_roles_string = ",".join([x.role.lower() for x in dtp_participants if x.role])
    dtp_vehicles_categories_string = ",".join(
        [x.category.name for x in models.Vehicle.objects.filter(participant__in=dtp_participants) if
         x.category]).lower()
    all_tags_string = ";".join([x.name for x in dtp.tags.all()]).lower()

    dtp.participant_categories.add(participant_categories.get("all"))

    if any("пешеход" in x.role.lower() for x in dtp_participants if x.role):
        dtp.participant_categories.add(participant_categories.get("pedestrians"))

    if any(x.lower() in dtp_participants_roles_string + dtp_vehicles_categories_string for x in ['велосипед']):
        dtp.participant_categories.add(participant_categories.get("velo"))

    if any(x.lower() in dtp_vehicles_categories_string for x in ['мотоцикл', 'мототранспорт', 'мопед', 'моторол']):
        dtp.participant_categories.add(participant_categories.get("moto"))

    if "до 16 лет" in all_tags_string:
        dtp.participant_categories.add(participant_categories.get("kids"))

    if any(x.lower() in dtp_vehicles_categories_string + all_tags_string for x in ['автобус', 'троллейбус', 'трамва']):
        dtp.participant_categories.add(participant_categories.get("public_transport"))