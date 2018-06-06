function validate_new_order(e) {
    //setTimeout(function () { validate_new_order_prime(e) }, 3000)
    validate_new_order_prime(e)
    return false;
}

function validate_new_order_prime(e) {
    e = e || window.event;
    if (!city_info.name) {
        return false;
    }
    var phone = document.getElementById('phone');
    var to_address = document.getElementById('to_address_1');
    var from_address = document.getElementById('from_address');
    setProperty(document.getElementById("from_not_found_error"), 'display', 'none');
    setProperty(document.getElementById("to_not_found_error"), 'display', 'none');
    setProperty(document.getElementById("from_empty_error"), 'display', 'none');
    setProperty(document.getElementById("to_empty_error"), 'display', 'none');
    setProperty(document.getElementById("phone_error"), 'display', 'none');
    setProperty(document.getElementById("not_uniq_error"), 'display', 'none');
    setProperty(document.getElementById("same_addresses_error"), 'display', 'none');
    if (from_address.value === '') {
        setAlert('from_empty_error');
        return false;
    }
    if (from_address.value === from_address_bad_value) {
        setAlert('from_not_found_error');
        return false;
    }
    if (from_address.value === to_address.value) {
        setAlert('same_addresses_error');
        return false;
    }
    if (to_address.value === '' && city_info.to_address_check) {
        setAlert('to_empty_error');
        return false;
    }
    if (to_address.value === to_1_address_bad_value && city_info.to_address_check) {
        setAlert('to_not_found_error');
        return false;
    }
    if (phone.value === '') {
        setAlert('phone_error');
        return false;
    }
    normal_phone = normalize_phone(phone)
    if ((normal_phone.length != 11 && normal_phone.length != city_info.phone_length_without_code + city_info.phone_code.toString().length)
        || normal_phone[0] != '8' || isNaN(normal_phone)) {
        setAlert('phone_error');
        return false;
    }
    document.getElementById('submitButton').disabled = true;
    loadSMSForm();
    return false;
}

function validate_cancel(e) {
    e = e || window.event;
    hide_notify();
    abortOrder();
    city_map();
    try { setProperty(document.getElementById("car"), 'display', 'none') } catch (e) { }
    return false;
}

function validate_sms_code(e) {
    e = e || window.event;
    setProperty(document.getElementById("wrong_code_error"), 'display', 'none');
    var code = document.getElementById('sms_code');
    document.getElementById('submitButton').disabled = true;
    loadFindCarForm()
    return false;
}

function validate_new_driver(){
	var phone = document.getElementById('phone');
	var surname = document.getElementById('surname');
	var firstname = document.getElementById('firstname');
	var patronymic = document.getElementById('patronymic');
	var mark = document.getElementById('mark');
	var color = document.getElementById('color');
	var gosnumber = document.getElementById('gosnumber');
	var city = document.getElementById('city');
	normal_phone = simple_normalize_phone(phone)
    if ((normal_phone.length != 11) || normal_phone[0] != '8' || isNaN(normal_phone)) {
        setProperty(document.getElementById("new_driver_notify_fail"), 'display', 'block');
		return false;
    }
	if(![phone.value,city.value].every(function(e){
		return e != ''
	})){
		setProperty(document.getElementById("new_driver_notify_fail"), 'display', 'block');
		return false;
	}
	phone.value = normal_phone;
    document.getElementById('submitButton').disabled = true;
	post('/new-driver', {
		phone: phone.value,
		surname: surname.value,
		firstname: firstname.value,
		patronymic: patronymic.value,
		mark: mark.value,
		color: color.value,
		gosnumber: gosnumber.value,
		city: city.value
	}, function(){});
	setProperty(document.getElementById("new_driver_notify_success"), 'display', 'block');
    return false;
}

function validate_feedback(){
	var phone = document.getElementById('phone');
	var firstname = document.getElementById('firstname');
  var message = document.getElementById('message');
	normal_phone = simple_normalize_phone(phone)
    if ((normal_phone.length != 11) || normal_phone[0] != '8' || isNaN(normal_phone)) {
        setProperty(document.getElementById("feedback_notify_fail"), 'display', 'block');
		return false;
    }
	if(![phone.value].every(function(e){
		return e != ''
	})){
		setProperty(document.getElementById("feedback_notify_fail"), 'display', 'block');
		return false;
	}
	phone.value = normal_phone;
    document.getElementById('submitButton').disabled = true;
	post('/send-feedback', {
		phone: phone.value,
		firstname: firstname.value,
		message: message.value
	}, function(){});
	setProperty(document.getElementById("feedback_notify_success"), 'display', 'block');
    return false;
}
