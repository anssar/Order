import random
import json
import requests

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings

from .models import City, BlackPhone
from .utils import send_email_feedback_util, set_city_util, checkOrderState, abortOrderUtil, humanize_phone, send_sms_util, send_email_util, top_addresses, route_analysis, address_correct, get_coords, create_order, uniqOrder, get_city_util, get_city_json_util, get_city_by_ip, get_city_by_city_for_select

CONFIRM_SMS = False

def nopage(request):
    return render(request, '404.html')

def nizhnevartovsk(request):
    set_city_util(request, 'Нижневартовск')
    return render(request, 'nizhnevartovsk.html')

def ekaterinburg(request):
    set_city_util(request, 'Екатеринбург')
    return render(request, 'ekaterinburg.html')

def magnitogorsk(request):
    set_city_util(request, 'Магнитогорск')
    return render(request, 'magnitogorsk.html')

def chelyabinsk(request):
    set_city_util(request, 'Челябинск')
    return render(request, 'chelyabinsk.html')

def sochi(request):
    set_city_util(request, 'Сочи')
    return render(request, 'sochi.html')

def bilimbay(request):
    set_city_util(request, 'Билимбай (Первоуральск ГО)')
    return render(request, 'bilimbay.html')

def langepas(request):
    set_city_util(request, 'Лангепас')
    return render(request, 'langepas.html')

def khanty_mansiysk(request):
    set_city_util(request, 'Ханты-Мансийск')
    return render(request, 'khanty_mansiysk.html')

def pervouralsk(request):
    set_city_util(request, 'Первоуральск')
    return render(request, 'pervouralsk.html')

def uralmash(request):
    set_city_util(request, 'Екатеринбург')
    return render(request, 'uralmash.html')

def paycard(request):
    return render(request, 'paycard.html')

def telegram(request):
    return render(request, 'telegram.html')


def mainPage(request):
    request.session.set_expiry(3600)
    try:
        city = request.GET.get('city')
        if city:
            set_city_util(request, city)
    except:
        pass
    if request.META.get('HTTP_HOST', '').find('app.fishka.taxi') != -1:
        return redirect('http://fishka.taxi/app')
    if request.META.get('HTTP_HOST', '').find('driver.fishka.taxi') != -1:
        return driver(request)
    if (request.is_mobile and request.META.get('HTTP_HOST', '').find('m.fishka.taxi') == -1
    and request.META.get('HTTP_HOST', '').find('fishka.taxi') != -1):
        try:
            city = json.loads(request.session.get('status')).get('city', 'Екатеринбург')
        except:
            city = 'Екатеринбург'
        return redirect('http://m.fishka.taxi?city=' + city)
    if (request.is_mobile and request.META.get('HTTP_HOST', '').find('m.taxifishka.com') == -1
    and request.META.get('HTTP_HOST', '').find('taxifishka.com') != -1):
        try:
            city = json.loads(request.session.get('status')).get('city', 'Екатеринбург')
        except:
            city = 'Екатеринбург'
        return redirect('http://m.taxifishka.com?city=' + city)
    if (request.META.get('HTTP_HOST', '').find('xn----7sbb4ahczhphi') != -1
    and request.session.get('uralmash_flag') is None):
        request.session['uralmash_flag'] = True
        return redirect('/uralmash')
    if (request.META.get('HTTP_HOST', '').find('xn----7sbba1blki7ahir4e') != -1
    and request.session.get('uralmash_flag') is None):
        request.session['uralmash_flag'] = True
        return redirect('/uralmash')
    if (request.META.get('HTTP_HOST', '').find('xn----7sbb4ajih0bg2eybk') != -1
    and request.session.get('uralmash_flag') is None):
        request.session['uralmash_flag'] = True
        return redirect('/uralmash')
    if (request.META.get('HTTP_HOST', '').find('xn----7sbbh2able7abubhcji') != -1
    and request.session.get('uralmash_flag') is None):
        request.session['uralmash_flag'] = True
        return redirect('/uralmash')
    if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1 or
    request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
        return render(request, 'mobile_index.html')
    else:
        return render(request, 'index.html')

def toFullVersion(request):
    try:
        city = request.GET.get('city')
        if city:
            set_city_util(request, city)
    except:
        pass
    try:
        city = json.loads(request.session.get('status')).get('city', 'Екатеринбург')
    except:
        city = 'Екатеринбург'
    if request.session.get('full_version_flag') is not None:
        if request.META.get('HTTP_HOST', '').find('fishka.taxi') != -1:
            return redirect('http://fishka.taxi?city=' + city)
        return redirect('http://taxifishka.com?city=' + city)
    request.session['full_version_flag'] = True
    if request.META.get('HTTP_HOST', '').find('fishka.taxi') != -1:
        return redirect('http://fishka.taxi/to-full-version?city=' + city)
    return redirect('http://taxifishka.com/to-full-version?city=' + city)

def toMobileVersion(request):
    try:
        city = request.GET.get('city')
        if city:
            set_city_util(request, city)
    except:
        pass
    try:
        city = json.loads(request.session.get('status')).get('city', 'Екатеринбург')
    except:
        city = 'Екатеринбург'
    if request.session.get('full_version_flag') is not None:
        del request.session['full_version_flag']
    if request.META.get('HTTP_HOST', '').find('fishka.taxi') != -1:
        return redirect('http://m.fishka.taxi?city=' + city)
    return redirect('http://m.taxifishka.com/?city=' + city)

def checkOrderStateChange(request):
    status = request.session.get('status')
    if status is None:
        return HttpResponse('Yes')
    info = json.loads(status)
    if info['step'] == 1 or info['step'] == 2:
        return HttpResponse('Yes')
    order_id = info['data']['order_id']
    changed, hard = checkOrderState(order_id, info, info['city'])
    if changed:
        request.session['status'] = json.dumps(info)
        if hard:
            return HttpResponse('Hard')
        else:
            return HttpResponse('Yes')
    return HttpResponse('No')

def getCarCoords(request):
    status = request.session.get('status')
    if status is None:
        return HttpResponse(json.dumps({'status': 'Fail', 'coord':{}}))
    info = json.loads(status)
    if info['step'] == 1 or info['step'] == 2 or info['step'] == 3:
        return HttpResponse(json.dumps({'status': 'Fail', 'coord':{}}))
    try:
        return HttpResponse(json.dumps({'status': 'OK', 'coord':{
            'lat': info['data']['crew_coord']['lat'],
            'lon': info['data']['crew_coord']['lon']}}))
    except:
        return HttpResponse(json.dumps({'status': 'Fail_d', 'coord':{}}))
        #return HttpResponse(json.dumps({'status': 'OK', 'coord':{
        #    'lat': info['data']['route'][0]['lat'] + random.random(),
        #    'lon': info['data']['route'][0]['lon'] + random.random()}}))

def abortOrder(request):
    status = request.session.get('status')
    if status is None:
        return newOrderForm(request)
    info = json.loads(status)
    if info['step'] == 1 or info['step'] == 2:
        return newOrderForm(request)
    order_id = info['data']['order_id']
    abortOrderUtil(order_id)
    return redirect('/new-order-form')

def failNotify(request):
    status = request.session.get('status')
    if status is None:
        return  HttpResponse('')
    info = json.loads(status)
    if info['step'] != 7:
        return  HttpResponse('')
    if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
    or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
        return render(request, 'mobile_failNotify.html')
    else:
        return render(request, 'failNotify.html')

def successNotify(request):
    status = request.session.get('status')
    if status is None:
        return  HttpResponse('')
    info = json.loads(status)
    if info['step'] != 8:
        return  HttpResponse('')
    if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
    or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
        return render(request, 'mobile_successNotify.html')
    else:
        return render(request, 'successNotify.html')

def getCoordsFromCookie(request):
    status = request.session.get('status')
    if status is None:
        return HttpResponse(json.dumps([]))
    if json.loads(status)['step'] == 1:
        return HttpResponse(json.dumps([]))
    return HttpResponse(json.dumps(json.loads(status)['data']['route']))

def getStep(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
        return HttpResponse('1')
    return HttpResponse(json.dumps(json.loads(status)['step']))


def currentForm(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
        return newOrderForm(request)
    info = json.loads(status)
    if info['step'] == 7 or info['step'] == 8:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
        return redirect('/new-order-form/')
    if info['step'] == 1:
        if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
        or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
            return render(request, 'mobile_newOrderForm.html', {'cities': City.objects.all(),
                                                                'default': info['city']})
        else:
            return render(request, 'newOrderForm.html', {'cities': City.objects.all(),
                                                         'default': info['city']})
    if info['step'] == 2:
        if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
        or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
            return render(request, 'mobile_confirmSMSForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                      'attempt': info['data']['attempt_sms']})
        else:
            return render(request, 'confirmSMSForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                      'attempt': info['data']['attempt_sms']})
    if info['step'] == 3:
        if request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1:
            return render(request, 'mobile_findCarForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'from_address': info['data']['from_address'].split(' *')[0]})
        else:
            return render(request, 'findCarForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'from_address': info['data']['from_address'].split(' *')[0]})
    if info['step'] == 4:
        if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
        or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
            return render(request, 'mobile_carGoToYouForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'sum': (str(info['data']['sum']) + ' руб.') if str(info['data']['sum']) != '0' else 'Окончательная цена по итогу поездки',
                                                'mark': info['data']['mark'],
                                                'model': info['data']['model'],
                                                'color': info['data']['color'],
                                                'gos_number': info['data']['gos_number'],
                                                'from_address': info['data']['from_address'].split(' *')[0]})
        else:
            return render(request, 'carGoToYouForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'sum': (str(info['data']['sum']) + ' руб.') if str(info['data']['sum']) != '0' else 'Окончательная цена по итогу поездки',
                                                'mark': info['data']['mark'],
                                                'model': info['data']['model'],
                                                'color': info['data']['color'],
                                                'gos_number': info['data']['gos_number'],
                                                'from_address': info['data']['from_address'].split(' *')[0]})
    if info['step'] == 5:
        if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
        or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
            return render(request, 'mobile_carWaitForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'sum': (str(info['data']['sum']) + ' руб.') if str(info['data']['sum']) != '0' else 'Окончательная цена по итогу поездки',
                                                'mark': info['data']['mark'],
                                                'model': info['data']['model'],
                                                'color': info['data']['color'],
                                                'gos_number': info['data']['gos_number'],
                                                'from_address': info['data']['from_address'].split(' *')[0]})
        else:
            return render(request, 'carWaitForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'sum': (str(info['data']['sum']) + ' руб.') if str(info['data']['sum']) != '0' else 'Окончательная цена по итогу поездки',
                                                'mark': info['data']['mark'],
                                                'model': info['data']['model'],
                                                'color': info['data']['color'],
                                                'gos_number': info['data']['gos_number'],
                                                'from_address': info['data']['from_address'].split(' *')[0]})
    if info['step'] == 6:
        if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
        or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
            return render(request, 'mobile_clientInCarForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'sum': (str(info['data']['sum']) + ' руб.') if str(info['data']['sum']) != '0' else 'Окончательная цена по итогу поездки',
                                                'mark': info['data']['mark'],
                                                'model': info['data']['model'],
                                                'color': info['data']['color'],
                                                'gos_number': info['data']['gos_number'],
                                                'from_address': info['data']['from_address'].split(' *')[0]})
        else:
            return render(request, 'clientInCarForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'sum': (str(info['data']['sum']) + ' руб.') if str(info['data']['sum']) != '0' else 'Окончательная цена по итогу поездки',
                                                'mark': info['data']['mark'],
                                                'model': info['data']['model'],
                                                'color': info['data']['color'],
                                                'gos_number': info['data']['gos_number'],
                                                'from_address': info['data']['from_address'].split(' *')[0]})
    return HttpResponse('')

def confirmForm(request):
    status = request.session.get('status')
    if status is None:
        return currentForm(request)
    info = json.loads(status)
    city = get_city_util(info['city'])
    comment = str.strip(request.POST.get('comment', ''))
    phone = str.strip(request.POST.get('phone', ''))
    from_address = str.strip(request.POST.get('from_address', ''))
    to_address = str.strip(request.POST.get('to_address', ''))
    try:
        if from_address.find('/') == -1:
            from_address = from_address.split(',')[0] + ' /' + info['city'] + '/,' +  from_address.split(',')[1]
    except:
        pass
    try:
        if to_address.find('/') == -1:
            to_address = to_address.split(',')[0] + ' /' + info['city'] + '/,' +  to_address.split(',')[1]
    except:
        pass
    if not all([phone, from_address, to_address]):
        if not (not city.to_address_check and all([phone, from_address])):
            return currentForm(request)
    if info['step'] != 1:
        return currentForm(request)
    info['step'] = 2
    price, coords = route_analysis(from_address, to_address, info['city'])
    code = str(random.randint(100, 999))
    print(code)
    if CONFIRM_SMS:
        send_sms_util(phone, 'Ваш код: ' + code)
    if to_address:
        info['data'] = {'phone': phone, 'from_address': from_address, 'to_address': to_address,
                    'route':[get_coords(from_address, info['city'])[0], get_coords(to_address, info['city'])[0]],
                    'code': code, 'attempt': 3, 'comment': comment, 'sum': price,
                    'attempt_sms': 3}
    else:
        info['data'] = {'phone': phone, 'from_address': from_address, 'to_address': to_address,
                    'route':[get_coords(from_address, info['city'])[0]],
                    'code': code, 'attempt': 3, 'comment': comment, 'sum': price,
                    'attempt_sms': 3}
    request.session['status'] = json.dumps(info)
    if CONFIRM_SMS:
        if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
        or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
            return render(request, 'mobile_confirmSMSForm.html', {'phone': humanize_phone(phone), 'attempt': 3})
        else:
            return render(request, 'confirmSMSForm.html', {'phone': humanize_phone(phone), 'attempt': 3})
    else:
        return findCarForm(request)

@csrf_exempt
def setCity(request):
    city = str.strip(request.POST.get('city', ''))
    if not city:
        city = get_city_by_ip(request)
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': city})
    status = request.session.get('status')
    info = json.loads(status)
    city_name = get_city_by_city_for_select(city)
    info['city'] = city_name
    request.session['status'] = json.dumps(info)
    return HttpResponse('OK')

@csrf_exempt
def getCity(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
    status = request.session.get('status')
    info = json.loads(status)
    if not info.get('city', ''):
        info['city'] = get_city_by_ip(request)
    request.session['status'] = json.dumps(info)
    return HttpResponse(get_city_json_util(info['city']))


def newOrderForm(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
    status = request.session.get('status')
    info = json.loads(status)
    if not info.get('city', ''):
        info['city'] = get_city_by_ip(request)
    info['step'] = 1
    info['data'] = {}
    request.session['status'] = json.dumps(info)
    if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
    or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
        return render(request, 'mobile_newOrderForm.html', {'cities': City.objects.all(),
                                                            'default': info['city']})
    else:
        return render(request, 'newOrderForm.html', {'cities': City.objects.all(),
                                                     'default': info['city']})

def findCarForm(request):
    status = request.session.get('status')
    if status is None:
        return currentForm(request)
    info = json.loads(status)
    if info['step'] != 2:
        return currentForm(request)
    info['step'] = 3
    black_list = BlackPhone.objects.all()
    if info['data']['phone'] in [x.phone for x in black_list]:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': info['city']})
        return newOrderForm(request)
    if info['data']['comment']:
        order_id = create_order(info['data']['from_address'] + " *" + info['data']['comment'],
                            info['data']['to_address'], info['data']['phone'], info['city'])
    else:
        order_id = create_order(info['data']['from_address'],
                            info['data']['to_address'], info['data']['phone'], info['city'])
    if order_id == -1:
        return newOrderForm(request)
    info['data']['order_id'] = order_id
    request.session['status'] = json.dumps(info)
    if (request.META.get('HTTP_HOST', '').find('m.taxifishka.com') != -1
    or request.META.get('HTTP_HOST', '').find('m.fishka.taxi') != -1):
        return render(request, 'mobile_findCarForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'from_address': info['data']['from_address']})
    else:
        return render(request, 'findCarForm.html', {'phone': humanize_phone(info['data']['phone']),
                                                'from_address': info['data']['from_address']})

def checkCode(request):
    code = str.strip(request.POST.get('code', ''))
    if not code:
        return HttpResponse('Fail')
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
        return HttpResponse('Fail')
    info = json.loads(status)
    if info['step'] != 2:
        return HttpResponse('Fail')
    if info['data']['attempt'] == 0:
        return HttpResponse('Fail')
    if info['data']['code'] == code:
        return HttpResponse('OK')
    info['data']['attempt'] -= 1
    request.session['status'] = json.dumps(info)
    return HttpResponse('Fail')

def resendSMS(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
        return HttpResponse('Fail')
    info = json.loads(status)
    if info['step'] != 2:
        return HttpResponse('Fail')
    if info['data']['attempt_sms'] < 1:
        return HttpResponse('Fail')
    info['data']['attempt'] = 3
    info['data']['attempt_sms'] -= 1
    code = str(random.randint(100, 999))
    print(code)
    send_sms_util(info['data']['phone'], 'Ваш код: ' + code)
    info['data']['code'] = code
    request.session['status'] = json.dumps(info)
    return HttpResponse(str(info['data']['attempt_sms']))

def parseAddress(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
    status = request.session.get('status')
    info = json.loads(status)
    if not info.get('city', ''):
        info['city'] = get_city_by_ip(request)
    request.session['status'] = json.dumps(info)
    field = str.strip(request.POST.get('field', ''))
    token = str.strip(request.POST.get('response_id', ''))
    top = top_addresses(field, info['city'])
    return HttpResponse(json.dumps({'addresses': top, 'response_id': token}))

def checkCorrect(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
    status = request.session.get('status')
    info = json.loads(status)
    if not info.get('city', ''):
        info['city'] = get_city_by_ip(request)
    request.session['status'] = json.dumps(info)
    phone = str.strip(request.POST.get('phone', ''))
    from_address = str.strip(request.POST.get('from_address', ''))
    to_address = str.strip(request.POST.get('to_address', ''))
    comment = str.strip(request.POST.get('comment', ''))
    city = get_city_util(info['city'])
    try:
        if from_address.find('/') == -1:
            from_address = from_address.split(',')[0] + ' /' + info['city'] + '/,' +  from_address.split(',')[1]
    except:
        pass
    try:
        if to_address.find('/') == -1:
            to_address = to_address.split(',')[0] + ' /' + info['city'] + '/,' +  to_address.split(',')[1]
    except:
        pass
    if not all([phone, from_address, to_address]):
        if not (not city.to_address_check and all([phone, from_address])):
            return HttpResponse('fail_1')
    if from_address.lower() == to_address.lower():
        return HttpResponse('fail_4')
    if (not address_correct(from_address, info['city'])):
         return HttpResponse('fail_1')
    if city.to_address_check:
        if (not address_correct(to_address, info['city'])):
             return HttpResponse('fail_2')
    if not uniqOrder(from_address  + " *" + comment, to_address, phone, city.to_address_check):
        return HttpResponse('fail_3')
    return HttpResponse('OK')

def routeAnalysis(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
    status = request.session.get('status')
    info = json.loads(status)
    if not info.get('city', ''):
        info['city'] = get_city_by_ip(request)
    request.session['status'] = json.dumps(info)
    from_address = str.strip(request.POST.get('from_address', ''))
    to_address = str.strip(request.POST.get('to_address_1', ''))
    try:
        if from_address.find('/') == -1:
            from_address = from_address.split(',')[0] + ' /' + info['city'] + '/,' +  from_address.split(',')[1]
    except:
        pass
    try:
        if to_address.find('/') == -1:
            to_address = to_address.split(',')[0] + ' /' + info['city'] + '/,' +  to_address.split(',')[1]
    except:
        pass
    if ((not all([from_address, to_address])) or
        (not address_correct(from_address, info['city'])) or (not address_correct(to_address, info['city']))):
        if from_address and address_correct(from_address, info['city']):
            return HttpResponse(json.dumps({'price': 'Окончательная цена по итогу поездки.', 'route': get_coords(from_address, info['city']),
                                            'status': 1}))
        if to_address and address_correct(to_address, info['city']):
            return HttpResponse(json.dumps({'price': 'Окончательная цена по итогу поездки.', 'route': get_coords(to_address, info['city']),
                                            'status': 1}))
        return HttpResponse(json.dumps({'price': 'Окончательная цена по итогу поездки.', 'route': [], 'status': 0}))
    price, coords = route_analysis(from_address, to_address, info['city'])
    return HttpResponse(json.dumps({'price': str(price) + ' руб.', 'route': coords, 'status': 2}))

def drivers(request):
    return redirect(request.build_absolute_uri().replace('drivers', 'driver'))
    # try:
    #     city = request.GET.get('city')
    #     if city:
    #         set_city_util(request, city)
    # except:
    #     city = 'Екатеринбург'
    # return render(request, 'drivers.html', {'cities': City.objects.all(), 'default': city})

def driver(request):
    try:
        city = request.GET.get('city')
        if city:
            set_city_util(request, city)
    except:
        city = 'Екатеринбург'
    return render(request, 'driver.html', {'cities': City.objects.all(), 'default': city})

def operator(request):
    try:
        city = request.GET.get('city')
        if city:
            set_city_util(request, city)
    except:
        city = 'Екатеринбург'
    return render(request, 'operator.html', {'cities': City.objects.all(), 'default': city})

def feedback(request):
    try:
        city = request.GET.get('city')
        if city:
            set_city_util(request, city)
    except:
        city = 'Екатеринбург'
    return render(request, 'feedback.html', {'cities': City.objects.all(), 'default': city})

def new_driver(request):
    try:
        city = City.objects.get(name=str.strip(request.POST.get('city', '')))
    except:
        return HttpResponse('Fail')
    phone = str.strip(request.POST.get('phone', ''))
    surname = str.strip(request.POST.get('surname', ''))
    firstname = str.strip(request.POST.get('firstname', ''))
    patronymic = str.strip(request.POST.get('patronymic', ''))
    mark = str.strip(request.POST.get('mark', ''))
    color = str.strip(request.POST.get('color', ''))
    gosnumber = str.strip(request.POST.get('gosnumber', ''))
    gosnumber_sms = ''.join([x for x in gosnumber if x.isdigit()])
    if not all([phone]):
        return HttpResponse('Fail')
    hour = (timezone.now().hour + 5) % 24
    bphone = city.day_brigadier_phone
    if hour > 22 or hour < 10 and city.night_brigadier_phone:
        bphone = city.night_brigadier_phone
    if bphone:
        send_sms_util(bphone, ' '.join([city.name.split(' ')[0],phone,surname,firstname,patronymic,mark,color,gosnumber]))
    send_email_util(city.email, [surname,firstname,patronymic,phone,mark,color,gosnumber,city.name])
    send_sms_util(phone, 'Ожидайте звонок от таксиФИШКА.рф или позвоните нам ' + city.day_brigadier_phone)
    return HttpResponse('OK')

def send_feedback(request):
    phone = str.strip(request.POST.get('phone', ''))
    firstname = str.strip(request.POST.get('firstname', ''))
    message = str.strip(request.POST.get('message', ''))
    if not all([phone]):
        return HttpResponse('Fail')
    send_email_feedback_util(settings.EMAIL_HOST_USER, [firstname,phone,message])
    # send_email_feedback_util('rumyancevandr@yandex.ru', [firstname,phone,message])
    return HttpResponse('OK')
