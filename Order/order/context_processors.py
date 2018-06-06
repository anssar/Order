import json

from .models import City
from .utils import get_city_util, get_city_by_ip

def city(request):
    status = request.session.get('status')
    if status is None:
        request.session['status'] = json.dumps({'step': 1, 'data': {}, 'city': get_city_by_ip(request)})
    status = request.session.get('status')
    info = json.loads(status)
    if not info.get('city', ''):
        info['city'] = get_city_by_ip(request)
    request.session['status'] = json.dumps(info)
    city = get_city_util(info['city'])
    return {
        'city_name': city.name,
        'city_taxi_phone': city.taxi_phone,
        'city_tel_href': 'tel:' + city.taxi_phone,
    }
