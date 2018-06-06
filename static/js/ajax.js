function setCity(city) {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            loadCityInfo()
        }
    }
    var data = {'city': city}
    post('/set-city', data, finish)
}

function loadForm(onfinish, step) {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            document.getElementById("form_place").innerHTML = xhr.responseText
            onfinish(step)
        }
    }
    var data = {}
    post('/current-form', data, finish)
}

function loadOrderForm() {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            document.getElementById("form_place").innerHTML = xhr.responseText
            init_search()
            init_map()
            init_phone_controller()
            makeRing(1)
        }
    }
    var data = {}
    post('/new-order-form', data, finish)
}

function load_fail_notify() {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            document.getElementById("result_notify_place").innerHTML = xhr.responseText
        }
    }
    var data = {}
    post('/fail-notify', data, finish)
}

function load_success_notify() {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            document.getElementById("result_notify_place").innerHTML = xhr.responseText
        }
    }
    var data = {}
    post('/success-notify', data, finish)
}

function abortOrder() {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
          try {
              setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
          }
          catch(e){}
			document.getElementById("form_place").innerHTML = xhr.responseText
            init_search()
            init_map()
            init_phone_controller()
            makeRing(1)
        }
    }
    var data = {}
    post('/abort-order', data, finish)
}

function loadSMSForm() {
    var data = {}
    data['phone'] = normalize_phone(document.getElementById("phone"))
    data['from_address'] = document.getElementById("from_address").value
    data['to_address'] = document.getElementById("to_address_1").value
    data['comment'] = document.getElementById("comment").value
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            if (xhr.responseText === "OK") {
                var inner_finish = function (xhr) {
                    if (xhr.readyState == 4 && xhr.status == 200) {
                        document.getElementById("form_place").innerHTML = xhr.responseText
                        makeStepAction()
                    }
                }
                post('/confirm-form', data, inner_finish)
            }
            else {
                if (xhr.responseText === "fail_1") {
                    setAlert("from_not_found_error")
                    document.getElementById('submitButton').disabled = false;
                }
                if (xhr.responseText === "fail_2") {
                    setAlert("to_not_found_error")
                    document.getElementById('submitButton').disabled = false;
                }
                if (xhr.responseText === "fail_3") {
                    setAlert("not_uniq_error")
                    document.getElementById('submitButton').disabled = false;
                }
                if (xhr.responseText === "fail_4") {
                    setAlert("same_addresses_error")
                    document.getElementById('submitButton').disabled = false;
                }
            }
        }
    }
    post('/check-correct', data, finish)
}

function loadFindCarForm() {
    var data = {}
    data['code'] = document.getElementById("sms_code").value
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            if (xhr.responseText === "OK") {
                var inner_finish = function (xhr) {
                    if (xhr.readyState == 4 && xhr.status == 200) {
                        document.getElementById("form_place").innerHTML = xhr.responseText
                        makeStepAction()
                    }
                }
                post('/find-car-form', data, inner_finish)
            }
            else {
                setProperty(document.getElementById("wrong_code_error"), 'display', 'block');
                setProperty(document.getElementById("submitButton"), 'display', 'none');
                setProperty(document.getElementById("inactiveSubmitButton"), 'display', 'inline');
                bad_code = true;
                document.getElementById("sms_code").value = ''
                document.getElementById('submitButton').disabled = false;
                attempt_limit_count -= 1

            }
        }
    }
    post('/check-code', data, finish)
}

function makeStepAction() {
    var data = {}
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var step = parseInt(xhr.responseText);
            if (step === 2) {
                try {
		                setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
                }
                catch(e){}
                init_map()
                init_code_controller()
                makeRing(2)
                setProperty(document.getElementById("submitButton"), 'display', 'inline');
                setProperty(document.getElementById("inactiveSubmitButton"), 'display', 'none');
            }
            if (step === 3) {
              try {
                  setProperty(document.getElementById("mobile-version-button"), 'display', 'none');
              }
              catch(e){}
                bad_code = false;
                init_map()
                setTimeout(function () { makeRing(3) }, 2000)
                setTimeout(checkOrderState, 5000)
            }
        }
    }
    post('/get-step', data, finish)
}

function resendSMS() {
    var data = {}
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            if (xhr.responseText === "Fail") {
                setProperty(document.getElementById("resend_div"), 'display', 'none');
                return
            }
            else {
                attempt_limit_count = 3
                if (xhr.responseText === "-1" || xhr.responseText === "0") {
                    document.getElementById("attempt_count").innerHTML = "0"
                    setProperty(document.getElementById("resend_div"), 'display', 'none');
                }
                else {
                    document.getElementById("attempt_count").innerHTML = xhr.responseText
                }
            }
        }
    }
    post('/resend-sms', data, finish)
}
