﻿import operator
import datetime
import json
from ipwhois import IPWhois

from django.core import serializers
from django.core.mail import send_mail
from django.conf import settings

from .models import City
from .taximaster.api import get_order_state, change_order_state, send_sms, get_current_orders, get_addresses_like_street, get_addresses_like_house, analyze_route2, calc_order_cost2, create_order2, get_addresses_like_points, create_order_api

HOST = 'https://fishka.dyndns.org'
PORT = 8089
API_KEY = '4aaoI4Pp8m98XBjT55BYL57lj09XF9fa1b5E0SaA'

DEFAULT_CITY = 'Екатеринбург'


def humanize_phone(phone):
    # return phone[0] + '(' + phone[1:4] + ')' + phone[4:]
    return phone


def send_sms_util(phone, message):
    answer = send_sms(HOST, PORT, API_KEY, phone, message)
    if answer['code'] != 0:
        return False
    return True


def leve_dist(a, b):
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + \
                1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


def tokenize_address(address):
    street = ''
    house = ''
    city = ''
    i = 0
    try:
        while not address[i].isalpha():
            i += 1
        # while address[i].isalpha():
        #    street += address[i]
        #    i += 1
        while not address[i].isdigit():
            street += address[i]
            i += 1
        while address[i].isdigit():
            house += address[i]
            i += 1
        if (address[i] in ' /\\') or address[i].isalpha():
            house += address[i]
            i += 1
        while address[i].isdigit():
            house += address[i]
            i += 1
        city = address[i:]
    except IndexError:
        return normalize_street(street), house, city
    return normalize_street(street), house, city


def normalize_street(street):
    oldstreet = street
    street = ''
    for i in oldstreet:
        if i.isalpha() or i.isspace() or i.isdigit():
            street += i
        else:
            street += ' '
    while street.find('  ') != -1:
        street = street.replace('  ', ' ')
    return str.rstrip(street)


def get_top_streets(streets, street):
    dists = {}
    for t_street in streets:
        ct_street = t_street['street'].split(' /')[0]
        dists[t_street['street']] = leve_dist(
            ct_street.lower(), street.lower())
    return [x[0] for x in sorted(dists.items(), key=operator.itemgetter(1))[:5]]


def get_top_points(points, point):
    dists = {}
    for t_point in points:
        dists[t_point] = leve_dist(t_point.lower(), point.lower())
    return [x[0] for x in sorted(dists.items(), key=operator.itemgetter(1))[:5]]


def get_top_houses(addresses, house):
    dists = {}
    for t_address in addresses:
        t_house = t_address['house']
        dists[t_house] = leve_dist(t_house.lower(), house.lower())
    if t_house[-1].isdigit():
        if t_house.find('/') == -1 and t_house.find('к.') == -1 and t_house.find('ко') == -1 and t_house.find('ст') == -1:
            dists[t_house] = dists[t_house] * 10000000 + int(t_house[-1])
        else:
            dists[t_house] = dists[t_house] * 10000
    else:
        dists[t_house] = dists[t_house] * 10 + ord(t_house[-1].lower())
    if t_house.lower() == house.lower():
        dists[t_house] = 0
    return [x[0] for x in sorted(dists.items(), key=operator.itemgetter(1))[:5]]


def filter_points(answer):
    correct_addresses = []
    for address in answer['data']['addresses']:
        if address['coords']['lon'] != 0 and address['street'].find('аэроп. К') == -1:
            correct_addresses.append(address)
    answer['data']['addresses'] = correct_addresses
    return answer


def get_streets_starts_with(answer, street):
    ret = []
    for address in answer['data']['addresses']:
        for st in address['street'].split(' /')[0].split(' '):
            if str.rstrip(st).lower().startswith(str.rstrip(street).lower()):
                ret.append(str.rstrip(address['street'].split(' /')[0]))
    return ret


def extract_streets(answer, street):
    ret = []
    for address in answer['data']['addresses']:
        ret.append(str.rstrip(address['street']))
    return ret


def get_streets(street, selected_city):
    parts = street.split(' ')
    ret = set()
    for part in parts:
        if len(part) < 1:
            continue
        answer = get_addresses_like_street(
            HOST, PORT, API_KEY, part, city=selected_city)
        if answer['code'] != 0:
            return []
        if len(ret) == 0:
            ret = set(extract_streets(answer, part))
        else:
            ret = ret.intersection(set(extract_streets(answer, part)))
        if len(ret) == 0:
            return []
    return list(ret)


def get_points(street, selected_city):
    parts = street.split(' ')
    ret = set()
    for part in parts:
        if len(part) < 2:
            continue
        answer = get_addresses_like_points(
            HOST, PORT, API_KEY, part, city=selected_city)
        if answer['code'] != 0:
            return []
        else:
            answer = filter_points(answer)
        if len(ret) == 0:
            ret = set(extract_streets(answer, part))
        else:
            ret = ret.intersection(set(extract_streets(answer, part)))
        if len(ret) == 0:
            return []
    return list(ret)


def top_addresses(address, selected_city):
    address = address.lower()
    address = address.replace('пр-т', '')
    address = address.replace('ул.', '')
    street, house, city = tokenize_address(address)
    house = house.replace(' ', '')
    street = str.strip(street)
    if house == '' or house == '1905':
        streets = get_streets(street, selected_city)[:5]
        points = get_top_points(get_points(street, selected_city), street)
        return [x.split(' /')[0] for x in streets + points]
    top_streets = get_streets(street, selected_city)[:5]
    if len(top_streets) == 0:
        points = get_top_points(get_points(street, selected_city), street)
        return [x.split(' /')[0] for x in points]
    top = []
    cur_street_index = -1
    for cur_street in top_streets:
        cur_street_index += 1
        answer = get_addresses_like_house(
            HOST, PORT, API_KEY, cur_street, house, city=selected_city)
        if answer['code'] != 0:
            answer = get_addresses_like_house(
                HOST, PORT, API_KEY, cur_street, house.upper(), city=selected_city)
        if answer['code'] != 0:
            continue
        else:
            top_houses = get_top_houses(answer['data']['addresses'], house)
            top_exstension = [cur_street + ', ' + x for x in top_houses]
            if top_houses[0].lower() == str.strip(house).lower():
                try:
                    tmp = top[cur_street_index]
                    top[cur_street_index] = top_exstension[0]
                    top_exstension[0] = tmp
                except:
                    pass
            top.extend(top_exstension)
    return top[:5]


def top_addresses_for_all_city(address, selected_city):
    address = address.lower()
    street, house, city = tokenize_address(address)
    t_street = street
    top_streets = []
    while len(t_street) != 0:
        answer = get_addresses_like_street(
            HOST, PORT, API_KEY, t_street, city=selected_city)
        if answer['code'] != 0:
            t_street = t_street[:-1]
        else:
            top_streets = get_top_streets(answer['data']['addresses'], street)
            break
    if top_streets == []:
        return []
    if house == '':
        return [x.split(' /')[0] for x in top_streets]
    top = []
    cur_street_index = -1
    for cur_street in top_streets:
        cur_street_index += 1
        top_houses = []
        t_house = house
        while len(t_house) != 0:
            answer = get_addresses_like_house(
                HOST, PORT, API_KEY, cur_street, t_house, city=selected_city)
            if answer['code'] != 0:
                t_house = t_house[:-1]
            else:
                top_houses = get_top_houses(answer['data']['addresses'], house)
                break
        if top_houses == []:
            continue
        else:
            top_exstension = [cur_street + ', ' + x for x in top_houses]
            if top_houses[0] == str.strip(t_house):
                try:
                    tmp = top[cur_street_index]
                    top[cur_street_index] = top_exstension[0]
                    top_exstension[0] = tmp
                except:
                    pass
            top.extend(top_exstension)
    return top[:5]


def get_info(address, selected_city):
    street, house, city = tokenize_address(address)
    if len(address.split(', ')) > 1:
        house = address.split(', ')[-1]
        street = ', '.join(address.split(', ')[:-1])
        answer = get_addresses_like_house(
            HOST, PORT, API_KEY, street, house, city=selected_city)
        if answer['code'] != 0:
            return None
    else:
        answer = get_addresses_like_points(
            HOST, PORT, API_KEY, address, city=selected_city)
        if answer['code'] != 0:
            return None
    ret = {}
    ret['address'] = address
    good_index = 0
    for i in range(len(answer['data']['addresses'])):
        if answer['data']['addresses'][i]['house'].replace(' ', '').lower() == house:
            good_index = i
    ret['lon'] = answer['data']['addresses'][good_index]['coords']['lon']
    ret['lat'] = answer['data']['addresses'][good_index]['coords']['lat']
    return ret


def address_correct(address, selected_city):
    if len(address.split(', ')) > 1:
        house = address.split(', ')[-1]
        street = ', '.join(address.split(', ')[:-1])
        answer = get_addresses_like_house(
            HOST, PORT, API_KEY, street, house, city=selected_city)
        if answer['code'] != 0:
            return False
        return True
    else:
        answer = get_addresses_like_points(
            HOST, PORT, API_KEY, address, city=selected_city)
        if answer['code'] != 0:
            return False
        if answer['data']['addresses'][0]['coords']['lon'] == 0:
            return False
        return True


def route_analysis(from_address, to_address, selected_city):
    city = get_city_util(selected_city)
    from_info = get_info(from_address, selected_city)
    to_info = get_info(to_address, selected_city)
    if not all([from_info, to_info]):
        return 0, []
    answer = analyze_route2(HOST, PORT, API_KEY, [from_info, to_info])
    if answer['code'] != 0 and answer['code'] != 100:
        return 0, []
    route = answer['data'].get('full_route_coords', [
        {'lat': x['lat'], 'lon': x['lon']} for x in [from_info, to_info]
    ])
    params = {}
    if city.tarif:
        params['tariff_id'] = city.tarif
    if city.group_id:
        params['crew_group_id'] = city.group_id
    params['source_time'] = get_source_time()
    params['source_zone_id'] = answer['data']['addresses'][0]['zone_id']
    params['dest_zone_id'] = answer['data']['addresses'][1]['zone_id']
    params['distance_city'] = answer['data']['city_dist']
    params['distance_country'] = answer['data']['country_dist']
    if answer['data']['country_dist'] > 0:
        params['is_country'] = True
    params['source_distance_country'] = answer['data']['source_country_dist']
    answer = calc_order_cost2(HOST, PORT, API_KEY, params)
    if answer['code'] != 0:
        return 0, []
    return answer['data']['sum'], route


def get_coords(address, selected_city):
    if address == '':
        return [{'lat': 0, 'lon': 0}]
    street, house, city = tokenize_address(address)
    if len(address.split(', ')) > 1:
        house = address.split(', ')[-1]
        street = ', '.join(address.split(', ')[:-1])
        answer = get_addresses_like_house(
            HOST, PORT, API_KEY, street, house, city=selected_city)
        if answer['code'] != 0:
            return [{'lat': 0, 'lon': 0}]
    else:
        answer = get_addresses_like_points(
            HOST, PORT, API_KEY, address, city=selected_city)
        if answer['code'] != 0:
            return [{'lat': 0, 'lon': 0}]
    good_index = 0
    for i in range(len(answer['data']['addresses'])):
        if answer['data']['addresses'][i]['house'].replace(' ', '').lower() == house:
            good_index = i
    return [{'lon': answer['data']['addresses'][good_index]['coords']['lon'],
             'lat': answer['data']['addresses'][good_index]['coords']['lat']}]


def uniqOrder(from_address, to_address, phone, check_to):
    answer = get_current_orders(HOST, PORT, API_KEY, phone)
    if answer['code'] != 0:
        return False
    for order in answer['data']['orders']:
        if (order['source'].split(' *')[0] == from_address.split(' *')[0]):
            if check_to:
                if order['destination'] == to_address:
                    return False
            else:
                return False
    return True


def create_order(from_address, to_address, phone, selected_city):
    city = get_city_util(selected_city)
    if not uniqOrder(from_address, to_address, phone, city.to_address_check):
        return -1
    from_info = get_info(from_address.split(" *")[0], selected_city)
    if to_address:
        to_info = get_info(to_address, selected_city)
    else:
        to_info = None
    if to_info:
        answer = analyze_route2(HOST, PORT, API_KEY, [from_info, to_info])
        if answer['code'] != 0:
            return -1
        params = {}
        if city.tarif:
            params['tariff_id'] = city.tarif
        params['addresses'] = answer['data']['addresses']
        params['addresses'][0]['address'] = from_address
        params['addresses'][1]['address'] = to_address
        params['phone'] = phone
        params['source_time'] = get_source_time()
        params['crew_group_id'] = city.group_id
        answer = create_order2(HOST, PORT, API_KEY, params)
        if answer['code'] != 0:
            return -1
        return answer['data']['order_id']
    else:
        params = {}
        if city.tarif:
            params['tariff_id'] = city.tarif
        params['source'] = from_address
        params['phone'] = phone
        params['source_time'] = get_source_time()
        params['crew_group_id'] = city.group_id
        answer = create_order_api(HOST, PORT, API_KEY, params)
        if answer['code'] != 0:
            return -1
        return answer['data']['order_id']


def get_source_time():
    ret = ''
    now = datetime.datetime.now() + datetime.timedelta(minutes=10, hours=10)
    ret += str(now.year)
    ret += '0' * (2 - len(str(now.month))) + str(now.month)
    ret += '0' * (2 - len(str(now.day))) + str(now.day)
    ret += '0' * (2 - len(str(now.hour))) + str(now.hour)
    ret += '0' * (2 - len(str(now.minute))) + str(now.minute)
    ret += '0' * (2 - len(str(now.second))) + str(now.second)
    return ret


def abortOrderUtil(order_id):
    answer = change_order_state(HOST, PORT, API_KEY, order_id, 83)


def checkOrderState(order_id, info, selected_city):
    ret = False
    ret2 = False
    answer = get_order_state(HOST, PORT, API_KEY, order_id)
    if answer['code'] != 0:
        info['step'] = 7
        return True, False
    if answer['data']['state_kind'] == 'aborted':
        info['step'] = 7
        ret = True
    if answer['data']['state_kind'] == 'finished':
        info['step'] = 8
        ret = True
    if answer['data']['state_kind'] == 'new_order':
        if info['step'] == 3:
            if info['data']['from_address'] != answer['data']['source']:
                info['data']['from_address'] = answer['data']['source']
                info['data']['route'][0] = get_coords(
                    answer['data']['source'].split(' *')[0], selected_city)[0]
                ret = True
                ret2 = True
            if info['data']['to_address'] != answer['data']['destination']:
                info['data']['to_address'] = answer['data']['destination']
                try:
                    info['data']['route'][1] = get_coords(
                        answer['data']['destination'], selected_city)[0]
                except:
                    pass
                ret = True
                ret2 = True
            if info['data']['phone'] != answer['data']['phone']:
                info['data']['phone'] = answer['data']['phone']
                ret = True
        else:
            info['data']['from_address'] = answer['data']['source']
            info['data']['route'][0] = get_coords(
                answer['data']['source'].split(' *')[0], selected_city)[0]
            info['data']['to_address'] = answer['data']['destination']
            try:
                info['data']['route'][1] = get_coords(
                    answer['data']['destination'], selected_city)[0]
            except:
                pass
            info['data']['phone'] = answer['data']['phone']
            info['step'] = 3
            ret = True
    if answer['data']['state_kind'] == 'driver_assigned':
        try:
            if answer['data']['confirmed'] == 'not_confirmed':
                return False, False
        except:
            pass
        if info['step'] == 4:
            if info['data']['from_address'] != answer['data']['source']:
                info['data']['from_address'] = answer['data']['source']
                info['data']['route'][0] = get_coords(
                    answer['data']['source'].split(' *')[0], selected_city)[0]
                ret = True
                ret2 = True
            if info['data']['to_address'] != answer['data']['destination']:
                info['data']['to_address'] = answer['data']['destination']
                try:
                    info['data']['route'][1] = get_coords(
                        answer['data']['destination'], selected_city)[0]
                except:
                    pass
                ret = True
                ret2 = True
            if info['data']['phone'] != answer['data']['phone']:
                info['data']['phone'] = answer['data']['phone']
                ret = True
            if info['data']['mark'] != answer['data']['car_mark']:
                info['data']['mark'] = answer['data']['car_mark']
                ret = True
            if info['data']['model'] != answer['data']['car_model']:
                info['data']['model'] = answer['data']['car_model']
                ret = True
            if info['data']['color'] != answer['data']['car_color']:
                info['data']['color'] = answer['data']['car_color']
                ret = True
            if info['data']['gos_number'] != answer['data']['car_number']:
                info['data']['gos_number'] = answer['data']['car_number']
                ret = True
            if info['data']['crew_id'] != answer['data']['crew_id']:
                info['data']['crew_id'] = answer['data']['crew_id']
                ret = True
            try:
                if info['data']['crew_coord']['lat'] != answer['data']['crew_coords']['lat']:
                    info['data']['crew_coord']['lat'] = answer['data']['crew_coords']['lat']
                if info['data']['crew_coord']['lon'] != answer['data']['crew_coords']['lon']:
                    info['data']['crew_coord']['lon'] = answer['data']['crew_coords']['lon']
            except:
                pass
        else:
            info['data']['from_address'] = answer['data']['source']
            info['data']['route'][0] = get_coords(
                answer['data']['source'].split(' *')[0], selected_city)[0]
            info['data']['to_address'] = answer['data']['destination']
            try:
                info['data']['route'][1] = get_coords(
                    answer['data']['destination'], selected_city)[0]
            except:
                pass
            info['data']['phone'] = answer['data']['phone']
            info['data']['mark'] = answer['data']['car_mark']
            info['data']['model'] = answer['data']['car_model']
            info['data']['color'] = answer['data']['car_color']
            info['data']['gos_number'] = answer['data']['car_number']
            info['data']['crew_id'] = answer['data']['crew_id']
            info['data']['crew_coord'] = {}
            try:
                info['data']['crew_coord']['lat'] = answer['data']['crew_coords']['lat']
                info['data']['crew_coord']['lon'] = answer['data']['crew_coords']['lon']
            except:
                pass
            info['step'] = 4
            ret = True
    if answer['data']['state_kind'] == 'car_at_place':
        if info['step'] == 5:
            if info['data']['from_address'] != answer['data']['source']:
                info['data']['from_address'] = answer['data']['source']
                info['data']['route'][0] = get_coords(
                    answer['data']['source'].split(' *')[0], selected_city)[0]
                ret = True
                ret2 = True
            if info['data']['to_address'] != answer['data']['destination']:
                info['data']['to_address'] = answer['data']['destination']
                try:
                    info['data']['route'][1] = get_coords(
                        answer['data']['destination'], selected_city)[0]
                except:
                    pass
                ret = True
                ret2 = True
            if info['data']['phone'] != answer['data']['phone']:
                info['data']['phone'] = answer['data']['phone']
                ret = True
            if info['data']['mark'] != answer['data']['car_mark']:
                info['data']['mark'] = answer['data']['car_mark']
                ret = True
            if info['data']['model'] != answer['data']['car_model']:
                info['data']['model'] = answer['data']['car_model']
                ret = True
            if info['data']['color'] != answer['data']['car_color']:
                info['data']['color'] = answer['data']['car_color']
                ret = True
            if info['data']['gos_number'] != answer['data']['car_number']:
                info['data']['gos_number'] = answer['data']['car_number']
                ret = True
            if info['data']['crew_id'] != answer['data']['crew_id']:
                info['data']['crew_id'] = answer['data']['crew_id']
                ret = True
            try:
                if info['data']['crew_coord']['lat'] != answer['data']['crew_coords']['lat']:
                    info['data']['crew_coord']['lat'] = answer['data']['crew_coords']['lat']
                if info['data']['crew_coord']['lon'] != answer['data']['crew_coords']['lon']:
                    info['data']['crew_coord']['lon'] = answer['data']['crew_coords']['lon']
            except:
                pass
        else:
            info['data']['from_address'] = answer['data']['source']
            info['data']['route'][0] = get_coords(
                answer['data']['source'].split(' *')[0], selected_city)[0]
            info['data']['to_address'] = answer['data']['destination']
            try:
                info['data']['route'][1] = get_coords(
                    answer['data']['destination'], selected_city)[0]
            except:
                pass
            info['data']['phone'] = answer['data']['phone']
            info['data']['mark'] = answer['data']['car_mark']
            info['data']['model'] = answer['data']['car_model']
            info['data']['color'] = answer['data']['car_color']
            info['data']['gos_number'] = answer['data']['car_number']
            info['data']['crew_id'] = answer['data']['crew_id']
            info['data']['crew_coord'] = {}
            try:
                info['data']['crew_coord']['lat'] = answer['data']['crew_coords']['lat']
                info['data']['crew_coord']['lon'] = answer['data']['crew_coords']['lon']
            except:
                pass
            info['step'] = 5
            ret = True
    if answer['data']['state_kind'] == 'client_inside':
        if info['step'] == 6:
            if info['data']['from_address'] != answer['data']['source']:
                info['data']['from_address'] = answer['data']['source']
                info['data']['route'][0] = get_coords(
                    answer['data']['source'].split(' *')[0], selected_city)[0]
                ret = True
                ret2 = True
            if info['data']['to_address'] != answer['data']['destination']:
                info['data']['to_address'] = answer['data']['destination']
                try:
                    info['data']['route'][1] = get_coords(
                        answer['data']['destination'], selected_city)[0]
                except:
                    pass
                ret = True
                ret2 = True
            if info['data']['phone'] != answer['data']['phone']:
                info['data']['phone'] = answer['data']['phone']
                ret = True
            if info['data']['mark'] != answer['data']['car_mark']:
                info['data']['mark'] = answer['data']['car_mark']
                ret = True
            if info['data']['model'] != answer['data']['car_model']:
                info['data']['model'] = answer['data']['car_model']
                ret = True
            if info['data']['color'] != answer['data']['car_color']:
                info['data']['color'] = answer['data']['car_color']
                ret = True
            if info['data']['gos_number'] != answer['data']['car_number']:
                info['data']['gos_number'] = answer['data']['car_number']
                ret = True
            if info['data']['crew_id'] != answer['data']['crew_id']:
                info['data']['crew_id'] = answer['data']['crew_id']
                ret = True
            try:
                if info['data']['crew_coord']['lat'] != answer['data']['crew_coords']['lat']:
                    info['data']['crew_coord']['lat'] = answer['data']['crew_coords']['lat']
                if info['data']['crew_coord']['lon'] != answer['data']['crew_coords']['lon']:
                    info['data']['crew_coord']['lon'] = answer['data']['crew_coords']['lon']
            except:
                pass
        else:
            info['data']['from_address'] = answer['data']['source']
            info['data']['route'][0] = get_coords(
                answer['data']['source'].split(' *')[0], selected_city)[0]
            info['data']['to_address'] = answer['data']['destination']
            try:
                info['data']['route'][1] = get_coords(
                    answer['data']['destination'], selected_city)[0]
            except:
                pass
            info['data']['phone'] = answer['data']['phone']
            info['data']['mark'] = answer['data']['car_mark']
            info['data']['model'] = answer['data']['car_model']
            info['data']['color'] = answer['data']['car_color']
            info['data']['gos_number'] = answer['data']['car_number']
            info['data']['crew_id'] = answer['data']['crew_id']
            info['data']['crew_coord'] = {}
            try:
                info['data']['crew_coord']['lat'] = answer['data']['crew_coords']['lat']
                info['data']['crew_coord']['lon'] = answer['data']['crew_coords']['lon']
            except:
                pass
            info['step'] = 6
            ret = True
    return ret, ret2


def get_city_util(city):
    try:
        city = City.objects.get(name=city)
    except:
        city = City.objects.get(name=DEFAULT_CITY)
    return city


def get_city_by_city_for_select(city):
    try:
        city = City.objects.get(name_for_select=city)
    except:
        city = City.objects.get(name=DEFAULT_CITY)
    return city.name


def get_city_json_util(city):
    city = get_city_util(city)
    return serializers.serialize('json', [city, ])


def get_city_by_ip(request):
    return DEFAULT_CITY
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        result = IPWhois(ip).lookup()
    except IndexError:
        return DEFAULT_CITY
    return DEFAULT_CITY


NEW_DRIVER_TEMPLATE = '''С сайта taxifishka.com поступила заявка на приемку нового водителя
Город: {}
ФИО: {}
Телефон: {}
Автомобиль: {}'''

FEEDBACK_TAMPLATE = '''С сайта taxifishka.com пришел отзыв
Имя: {}
Телефон: {}

{}
'''


def send_email_util(email, data):
    if email == '':
        return
    send_mail('[Taxifishka]Новый водитель',
              NEW_DRIVER_TEMPLATE.format(data[7], ' '.join(
                  data[:3]), data[3], ' '.join(data[4:7])),
              settings.EMAIL_HOST_USER,
              [email],
              fail_silently=True)

def send_email_feedback_util(email, data):
    if email == '':
        return
    send_mail('[Taxifishka]Обратная связь',
              FEEDBACK_TAMPLATE.format(data[0], data[1], data[2]),
              settings.EMAIL_HOST_USER,
              [email],
              fail_silently=True)


def set_city_util(request, city):
    try:
        city_g = City.objects.get(name=city)
    except:
        return
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps(
            {'step': 1, 'data': {}, 'city': city})
    status = request.session.get('status')
    info = json.loads(status)
    info['city'] = city
    request.session['status'] = json.dumps(info)
