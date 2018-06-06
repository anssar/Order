var bad_code = false
var attempt_limit_count = 3;

var city_info = {};

function post(url, params, finish) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    var params_arr = [];
    for (var k in params) {
        params_arr.push(k + '=' + encodeURIComponent(params[k]));
    }
    var params_str = params_arr.join('&');
    xhr.send(params_str);
    xhr.onreadystatechange = function () { finish(xhr) };
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function setProperty(obj, property, value) {
    if (obj.style.setProperty)
        obj.style.setProperty(property, value);
    else if (obj.style.setAttribute) {
        var parts = property.split('-');
        var propertyCamelCase = parts[0];
        for (var i = 1; i < parts.length; i++) {
            propertyCamelCase += parts[i].charAt(0).toUpperCase() +
                parts[i].substr(1);
        }
        obj.style.setAttribute(propertyCamelCase, value);
    } else {
        console.log('setProperty not supported');
    }
}

function hide_notify() {
    notify = document.getElementById("notify")
    setProperty(notify, "display", "none")
    notify_close = document.getElementById("notify-close")
    notify_close.onclick = function () { }
    return false;
}

function show_notify(e) {
    e = e || window.event;
    notify = document.getElementById("notify")
    setProperty(notify, "display", "block")
    notify_close = document.getElementById("notify-close")
    notify_close.onclick = hide_notify
    return false;
}

function simple_normalize_phone(phone) {
    ret = phone.value
    if (phone.value.length == 0) {
        return ret;
    }
	var whiteList = ['(', ')', ' ', '-']
	whiteList.forEach(function(c){
		ret = ret.split(c).join('')
	})
    if ((ret.length == 11 || ret.length == 10 || ret.length == 12) && !isNaN(ret)) {
        if (ret.length == 10) {
            if (ret[0] == '8' || ret[0] == '7') {
                return ''
            }
            else {
                ret = '8' + ret;
            }
        }
        if (ret.length == 11) {
            if (ret[0] != '8' && ret[0] != '7') {
                return ''
            }
            if (ret[0] == '7') {
                ret = '8' + ret.slice(1)
            }
        }
        if (ret.length == 12) {
            if (ret[0] != '+' || ret[1] != '7') {
                return ''
            }
            ret = '8' + ret.slice(2)
        }
    }
	else{
		return ''
	}
    return ret
}


function normalize_phone(phone) {
    ret = phone.value
    if (!city_info.name) {
        return ret
    }
	var whiteList = ['(', ')', ' ', '-']
	whiteList.forEach(function(c){
		ret = ret.split(c).join('')
	})
    if (phone.value.length == 0) {
        return ret;
    }
    if ((phone.value.length == 11 || phone.value.length == 10 || phone.value.length == 12) && !isNaN(phone.value)) {
        if (phone.value.length == 10) {
            if (phone.value[0] == '8' || phone.value[0] == '7') {
                setAlert('phone_error')
            }
            else {
                ret = '8' + phone.value
            }
        }
        if (phone.value.length == 11) {
            if (phone.value[0] != '8' && phone.value[0] != '7') {
                setAlert('phone_error')
            }
            if (phone.value[0] == '7') {
                ret = '8' + phone.value.slice(1)
            }
        }
        if (phone.value.length == 12) {
            if (phone.value[0] != '+' || phone.value[1] != '7') {
                setAlert('phone_error')
            }
            ret = '8' + phone.value.slice(2)
        }

    }
    else {
        if ((phone.value.length == city_info.phone_length_without_code ||
            phone.value.length == city_info.phone_length_without_code + city_info.phone_code.toString().length ||
            phone.value.length == city_info.phone_length_without_code + city_info.phone_code.toString().length - 1) &&
            !isNaN(phone.value)) {
            if (phone.value.length == city_info.phone_length_without_code) {
                ret = city_info.phone_code.toString() + ret;
            }
            if (phone.value.length == city_info.phone_length_without_code + city_info.phone_code.toString().length) {
                if (!phone.value.startsWith(city_info.phone_code.toString())) {
                    setAlert('phone_error')
                }
            }
            if (phone.value.length == city_info.phone_length_without_code + city_info.phone_code.toString().length - 1) {
                if (!phone.value.startsWith(city_info.phone_code.toString().slice(1))) {
                    setAlert('phone_error')
                }
                else {
                    ret = '8' + phone.value;
                }
            }
        }
        else {
            setAlert('phone_error')
        }
    }
    return ret
}

function oninput_phone(phone) {
    setProperty(document.getElementById("phone_error"), 'display', 'none');
}

function onfocus_phone(phone) {
    setProperty(document.getElementById("phone_error"), 'display', 'none');
}

function init_phone_controller() {
    var phone = document.getElementById("phone")
    phone.oninput = function () { oninput_phone(phone) }
    phone.onblur = function () { setTimeout(function () { normalize_phone(phone) }, 200) }
    phone.onfocus = function () { onfocus_phone(phone) }
}

function oninput_code(code) {
    setProperty(document.getElementById("wrong_code_error"), 'display', 'none');
    bad_code = false
    if (code.value.length == 3 && $.isNumeric(code.value) && attempt_limit_count > 0) {
        setProperty(document.getElementById("submitButton"), 'display', 'inline');
        setProperty(document.getElementById("inactiveSubmitButton"), 'display', 'none');
    }
    else {
        setProperty(document.getElementById("submitButton"), 'display', 'none');
        setProperty(document.getElementById("inactiveSubmitButton"), 'display', 'inline');
    }
}

function onblur_code(code) {
    if (bad_code) {
        setProperty(document.getElementById("wrong_code_error"), 'display', 'block');
    }
}

function onfocus_code(code) {
    setProperty(document.getElementById("wrong_code_error"), 'display', 'none');
}

function init_code_controller() {
    attempt_limit_count = 3
    var code = document.getElementById("sms_code")
    code.oninput = function () { oninput_code(code) }
    code.onblur = function () { onblur_code(code) }
    code.onfocus = function () { onfocus_code(code) }
    var submitButton = document.getElementById("submitButton")
    submitButton.onclick = function () { document.getElementById("confirmSMSForm").onsubmit() }
}

function init() {
    loadCityInfo()
    setTimeout(function () {
        var data = {}
        var finish = function (xhr) {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var step = parseInt(xhr.responseText);
                init_by_step(step)
            }
        }
        post('/get-step', data, finish)
    }, 500)
}

function init_by_step(step) {
    if (step == 1) {
        try { map.bounds_changed = function () { } } catch (e) { }
        var onfinish = function (step) {
            init_search()
            init_map()
            init_phone_controller()
            makeRing(step)
        }
        loadForm(onfinish, step)
    }
    if (step == 2) {
      try {
          setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
      }
      catch(e){}
        try { map.bounds_changed = function () { } } catch (e) { }
        var onfinish = function (step) {
            init_map()
            init_code_controller()
            makeRing(step)
        }
        loadForm(onfinish, step)
    }
    if (step == 3) {
      try {
          setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
      }
      catch(e){}
        try { map.bounds_changed = function () { } } catch (e) { }
        var onfinish = function (step) {
            init_map()
            setTimeout(function () { makeRing(step) }, 2000)
            setTimeout(checkOrderState, 5000)
        }
        loadForm(onfinish, step)
    }
    if (step == 4) {
      try {
          setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
      }
      catch(e){}
        var onfinish = function (step) {
            init_map()
            centered_on_taxi = false;
            setTimeout(function () { addCarMarker(step) }, 2000)
            setTimeout(checkOrderState, 5000)
            makeRing(step)
        }
        loadForm(onfinish, step)
    }
    if (step == 5) {
      try {
          setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
      }
      catch(e){}
        var onfinish = function (step) {
            init_map()
            setTimeout(zoom_on_taxi, 2000)
            setTimeout(checkOrderState, 5000)
            makeRing(step)
        }
        loadForm(onfinish, step)
    }
    if (step == 6) {
      try {
          setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
      }
      catch(e){}
        var onfinish = function (step) {
            init_map()
            centered_on_taxi = false;
            setTimeout(function () { addCarMarker(step) }, 2000)
            setTimeout(checkOrderState, 5000)
            makeRing(step)
        }
        loadForm(onfinish, step)
    }
    if (step == 7) {
      try {
          setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
      }
      catch(e){}
        try { setProperty(document.getElementById("car"), 'display', 'none') } catch (e) { }
        try { map.bounds_changed = function () { } } catch (e) { }
        load_fail_notify()
        city_map()
        makeRing(step)
    }
    if (step == 8) {
      try {
          setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
      }
      catch(e){}
        try { setProperty(document.getElementById("car"), 'display', 'none') } catch (e) { }
        try { map.bounds_changed = function () { } } catch (e) { }
        load_success_notify()
        city_map()
        makeRing(step)
    }
}

function reinit() {
    document.getElementById("result_notify_place").innerHTML = ''
    init_by_step(1)
}

function sleep(ms) {
    ms += new Date().getTime();
    while (new Date() < ms) { }
}

function checkOrderState() {
    var data = {}
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            if (xhr.responseText === "No") {
                setTimeout(checkOrderState, 5000)
            }
            else {
                if (xhr.responseText === "Hard") {
                    map_inited = false;
                }
                init()
            }
        }
    }
    post('/check-order-state-change', data, finish)
}

function setAlert(alert_id) {
    if (alert_id == 'from_empty_error') {
        setProperty(document.getElementById("from_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("to_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("from_empty_error"), 'display', 'block');
        setProperty(document.getElementById("to_empty_error"), 'display', 'none');
        setProperty(document.getElementById("phone_error"), 'display', 'none');
        setProperty(document.getElementById("not_uniq_error"), 'display', 'none');
        setProperty(document.getElementById("same_addresses_error"), 'display', 'none');
    }
    if (alert_id == "from_not_found_error") {
        if(document.getElementById('from_empty_error').style.display === 'block'){
            return;
        }
        setProperty(document.getElementById("from_not_found_error"), 'display', 'block');
        setProperty(document.getElementById("to_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("to_empty_error"), 'display', 'none');
        setProperty(document.getElementById("phone_error"), 'display', 'none');
        setProperty(document.getElementById("not_uniq_error"), 'display', 'none');
        setProperty(document.getElementById("same_addresses_error"), 'display', 'none');
    }
    if (alert_id == "same_addresses_error") {
        if (document.getElementById('from_empty_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('from_not_found_error').style.display === 'block') {
            return;
        }
        setProperty(document.getElementById("to_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("to_empty_error"), 'display', 'none');
        setProperty(document.getElementById("phone_error"), 'display', 'none');
        setProperty(document.getElementById("not_uniq_error"), 'display', 'none');
        setProperty(document.getElementById("same_addresses_error"), 'display', 'block');
    }
    if (alert_id == "not_uniq_error") {
        if (document.getElementById('from_empty_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('from_not_found_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('same_addresses_error').style.display === 'block') {
            return;
        }
        setProperty(document.getElementById("to_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("to_empty_error"), 'display', 'none');
        setProperty(document.getElementById("phone_error"), 'display', 'none');
        setProperty(document.getElementById("not_uniq_error"), 'display', 'block');
    }
    if (alert_id == "to_empty_error") {
        if (document.getElementById('from_empty_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('from_not_found_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('same_addresses_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('not_uniq_error').style.display === 'block') {
            return;
        }
        setProperty(document.getElementById("to_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("to_empty_error"), 'display', 'block');
        setProperty(document.getElementById("phone_error"), 'display', 'none');
    }
    if (alert_id == "to_not_found_error") {
        if (document.getElementById('from_empty_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('from_not_found_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('same_addresses_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('not_uniq_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('to_empty_error').style.display === 'block') {
            return;
        }
        setProperty(document.getElementById("to_not_found_error"), 'display', 'block');
        setProperty(document.getElementById("phone_error"), 'display', 'none');
    }
    if (alert_id == "phone_error") {
        if (document.getElementById('from_empty_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('from_not_found_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('same_addresses_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('not_uniq_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('to_empty_error').style.display === 'block') {
            return;
        }
        if (document.getElementById('to_not_found_error').style.display === 'block') {
            return;
        }
        setProperty(document.getElementById("phone_error"), 'display', 'block');
    }
}

function set_header() {
    return
    try {
        document.getElementById('city-name-header').innerHTML = city_info.name
        document.getElementById('city-taxi-phone-header').innerHTML = city_info.taxi_phone
    }
    catch (e) {
        setTimeout(set_header, 500);
    }
}

function loadCityInfo() {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            city_info = JSON.parse(xhr.responseText)[0]['fields']
            set_header()
            city_map()
        }
    }
    data = {}
    post('/get-city', data, finish)
}

function get_option_by_html(html) {
    return html.split('</span>')[0].replace('<span>', '').replace(' ,', ',');
}

function create_option_html(opt) {
    var splited = opt.split('/');
    var opt_city = city_info.name;
    var opt_address = splited[0];
    if (splited[1]) {
        opt_city = splited[1]
    }
    if (splited[2]) {
        opt_address += splited[2];
    }
    return ('<span>' + opt_address + '</span>' + '<br>' + '<span style="color:grey">' + opt_city + '</span>').replace(' ,', ',');
}

function bind_create_driver_button(){
	document.getElementById('submitButton').onclick = function () { document.getElementById("newDriverForm").onsubmit() }
}

function bind_feedback_button(){
	document.getElementById('submitButton').onclick = function () { document.getElementById("feedbackForm").onsubmit() }
}

function close_new_driver_success_notify(){
	setProperty(document.getElementById("new_driver_notify_success"), 'display', 'none');
	document.getElementById('submitButton').disabled = false;
	document.getElementById('phone').value = '';
	document.getElementById('surname').value = '';
	document.getElementById('firstname').value = '';
	document.getElementById('patronymic').value = '';
	document.getElementById('mark').value = '';
	document.getElementById('color').value = '';
	document.getElementById('gosnumber').value = '';
	return false;
}

function close_new_driver_fail_notify(){
	setProperty(document.getElementById("new_driver_notify_fail"), 'display', 'none');
	return false;
}

function close_feedback_success_notify(){
	setProperty(document.getElementById("feedback_notify_success"), 'display', 'none');
	document.getElementById('submitButton').disabled = false;
	document.getElementById('phone').value = '';
	document.getElementById('firstname').value = '';
	document.getElementById('message').value = '';
	return false;
}

function close_feedback_fail_notify(){
	setProperty(document.getElementById("feedback_notify_fail"), 'display', 'none');
	return false;
}

function go_to_drivers_form(){
	//var href = "http://taxifishka.com/driver?city=" + city_info.name;
	window.location = '/driver?city=' + city_info.name;
}

function go_to_feedback_form(){
	//var href = "http://taxifishka.com/driver?city=" + city_info.name;
	window.location = '/feedback';
}

function back_to_main_page(){
	var cities_select = document.getElementById("city")
  var selected_city = cities_select.options[cities_select.selectedIndex].text;
	//var href = "http://taxifishka.com/?city=" + selected_city;
  if(window.location.host === 'driver.fishka.taxi'){
    window.location = "http://fishka.taxi/?city=" + selected_city;
  }
  else{
    window.location = '/?city=' + selected_city;
  }
}

function back_to_main_page2(){
  window.location = '/';
}


function call_to_taxi(){
  var phone = city_info.taxi_phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
  window.location.href="tel://"+phone;
}
