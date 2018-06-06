var map;
var mapProp;
var taxi_posll;
var from_pos = 0;
var to_pos = 0;
var clear_map = true;
var map_inited = false;
var centered_on_taxi = false;


function init_map() {
    try {
        if (!map_inited) {
            place_map_div()
            city_map()
            var finish = function (xhr) {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var route = JSON.parse(xhr.responseText)
                    if (route.length != 0) {
                        add_route(route)
                    }
                }
            }
            var data = {}
            post('/get-coords-from-cookie', data, finish)
            map_inited = true
        }
        window.onresize = function () { place_map_div(); google.maps.event.trigger(map, 'resize'); }
    }
    catch (e) { }
}

function place_map_div() {
    mapdiv = document.getElementById("googleMap")
    setProperty(mapdiv, "position", "absolute")
    setProperty(mapdiv, "width", $(document).width().toString() + "px")
    setProperty(mapdiv, "height", $(document).height().toString() + "px")
    setProperty(mapdiv, "left", "0")
    setProperty(mapdiv, "top", "0")
    setProperty(mapdiv, "z-index", "-100")
}

function city_map() {
    try {
        if (city_info.name) {
            mapProp = {
                center: new google.maps.LatLng(city_info.city_center_lat, city_info.city_center_lng),
                zoom: city_info.city_zoom,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                streetViewControl: false,
                mapTypeControl: false
            };
            map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
        }
        else {
            setTimeout(city_map, 1000)
        }
    }
    catch (e) { }
}

function add_marker(pos) {
    if (!map_inited) { return; }
    mapProp = {
        center: new google.maps.LatLng(pos['lat'], pos['lon']),
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false,
        mapTypeControl: false
    };
    map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(pos['lat'], pos['lon']),
        map: map
    })
}

function add_route(route) {
    if (!map_inited) { return; }
    var start_t = route[0]
    var dest_t = route[route.length - 1]
    var start = new google.maps.LatLng(start_t['lat'], start_t['lon']);
    var dest = new google.maps.LatLng(dest_t['lat'], dest_t['lon']);
    from_pos = start
    to_pos = dest
    var directionsService = new google.maps.DirectionsService;
    var directionsDisplay = new google.maps.DirectionsRenderer;
    var request = {
        origin: start,
        destination: dest,
        travelMode: google.maps.DirectionsTravelMode.DRIVING
    };
    directionsService.route(request, function (response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
        }
    });
    directionsDisplay.setMap(map);
    setTimeout(function(){normalize_map(start, dest)}, 1000)

}

function visible(posll) {
    if (!map_inited) { return true; }
    var p = calcPos(posll)
    if (p.x < 400 && p.y > $(document).height() - 400) {
        return false
    }
    if (p.x > $(document).width() - 150 && p.y > $(document).height() - 400) {
        return false
    }
    if (p.x < 0 || p.y < 0) {
        return false
    }
    if (p.x > $(document).width() || p.y > $(document).height()) {
        return false
    }
    return true
}

function normalize_map(start, dest) {
    if (!map_inited) { return; }
    if (!visible(start) || !visible(dest)) {
        //map.setZoom(map.getZoom() - 1)
    }

}

function calcPos(posll) {
    if (!map_inited) { return; }
    var bounds = map.getBounds()
    var ne = bounds.getNorthEast()
    var sw = bounds.getSouthWest()
    var north = Math.round(ne.lng() * 1000000000000)
    var south = Math.round(sw.lng() * 1000000000000)
    var east = Math.round(ne.lat() * 1000000000000)
    var west = Math.round(sw.lat() * 1000000000000)
    var poslat = Math.round(posll.lat() * 1000000000000)
    var poslng = Math.round(posll.lng() * 1000000000000)
    var width = $(document).width()
    var height = $(document).height()
    var y = Math.round(height * ((poslat - west) / (east - west)))
    var x = Math.round(width * ((poslng - south) / (north - south)))
    //alert(ne.lng().toString() + " " + sw.lng().toString())
    return {x:x, y:y}

}

function makeRing(step) {
    if (!map_inited) { return; }
    if (step != 3) {
        setProperty(document.getElementById("ring"), 'display', 'none');
        map.bounds_changed = function () { }
    }
    else {
        var data = {}
        var finish = function (xhr) {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var answer = JSON.parse(xhr.responseText)
                var pos = answer[0]
                var posll = new google.maps.LatLng(pos['lat'], pos['lon']);
                var point = calcPos(posll);
                setProperty(document.getElementById("ring"), 'left', Math.round(point.x).toString() + "px");
                setProperty(document.getElementById("ring"), 'bottom', Math.round(point.y).toString() + "px");
                setProperty(document.getElementById("ring"), 'display', 'block');
                map.bounds_changed = function () { makeRing(3) }
            }
        }
        post('/get-coords-from-cookie', data, finish)
    }
}

function addCarMarker(step) {
    if (!map_inited) { return; }
    if (step != 4 && step != 6) {
        setProperty(document.getElementById("car"), 'display', 'none');
        map.bounds_changed = function () { }
        return;
    }
    var data = {}
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var answer = JSON.parse(xhr.responseText)
            if (answer['status'] == 'OK') {
                var pos = answer['coord']
                var posll = new google.maps.LatLng(pos['lat'], pos['lon']);
                add_taxi_marker(posll)
                map.bounds_changed = function () { add_taxi_marker(posll) }
                setTimeout(function () { addCarMarker(step) }, 5000)
            }
            else {
                setProperty(document.getElementById("car"), 'display', 'none');
                map.bounds_changed = function () { }
                if (answer['status'] === 'Fail_d') {
                    setTimeout(function () { addCarMarker(step) }, 5000)
                }
            }
        }
    }
    post('/get-car-coords', data, finish)
}

function add_taxi_marker(pos) {
    if (!map_inited) { return; }
        taxi_posll = pos
        if (!centered_on_taxi) {
            map.setCenter(pos)
            map.setZoom(15)
            centered_on_taxi = true;
        }
        if (visible(pos)) {
            var point = calcPos(pos);
            setProperty(document.getElementById("car"), 'left', (Math.round(point.x)).toString() + "px");
            setProperty(document.getElementById("car"), 'bottom', (Math.round(point.y)).toString() + "px");
            setProperty(document.getElementById("car"), 'display', 'block');
        }
        else {
            setProperty(document.getElementById("car"), 'display', 'none');
        }
}

function zoom_on_taxi() {
    if (!map_inited) { return; }
    var data = {}
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var answer = JSON.parse(xhr.responseText)
            if (answer['status'] == 'OK') {
                var pos = answer['coord']
                var posll = new google.maps.LatLng(pos['lat'], pos['lon']);
                map.setCenter(posll)
                map.setZoom(17)
                centered_on_taxi = true
                add_taxi_marker(posll)
                map.bounds_changed = function () { add_taxi_marker(posll) }
            }
        }
    }
    post('/get-car-coords', data, finish)
}
