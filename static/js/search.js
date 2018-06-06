var last_from_response_id = 0;
var last_to_1_response_id = 0;
var from_address_selected = false;
var to_address_1_selected = false;
var from_address_bad_value = '****';
var to_1_address_bad_value = '****';
var from_address_last_focus_out_value = "****";
var to_1_address_last_focus_out_value = "****";
var selected_city = "****";

function reinit_vars() {
    last_from_response_id = 0;
    last_to_1_response_id = 0;
    from_address_selected = false;
    to_address_1_selected = false;
    from_address_bad_value = '****';
    to_1_address_bad_value = '****';
    from_address_last_focus_out_value = "****";
    to_1_address_last_focus_out_value = "****";
    selected_city = '****';
}

function set_address_not_selected(field) {
    if (field.id == "from_address") {
        from_address_selected = false;
    }
    if (field.id == "to_address_1") {
        to_address_1_selected = false;
    }
}

function set_address_selected(field) {
    if (field.id == "from_address") {
        from_address_selected = true;
    }
    if (field.id == "to_address_1") {
        to_address_1_selected = true;
    }
}

function set_last_field_response_id(field, n) {
    if (field.id == "from_address") {
        last_from_response_id = n;
    }
    if (field.id == "to_address_1") {
        last_to_1_response_id = n;
    }
}

function get_field_bad_value(field) {
    if (field.id == "from_address") {
        return from_address_bad_value;
    }
    if (field.id == "to_address_1") {
        return to_1_address_bad_value;
    }
}

function get_field_last_focus_out_value(field) {
    if (field.id == "from_address") {
        return from_address_last_focus_out_value;
    }
    if (field.id == "to_address_1") {
        return to_1_address_last_focus_out_value;
    }
}

function set_field_last_focus_out_value(field) {
    if (field.id == "from_address") {
        from_address_last_focus_out_value = field.value;
    }
    if (field.id == "to_address_1") {
        to_1_address_last_focus_out_value = field.value;
    }
}

function work_with_map(analysis_response) {
    //map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
    try {
        if (analysis_response['status'] == 2) {
            map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
            var waypoints_t = analysis_response['route']
            add_route(waypoints_t);
            clear_map = false;
        }
        if (analysis_response['status'] == 1) {
            map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
            var pos = analysis_response['route'][0]
            add_marker(pos);
            clear_map = false;
        }
        if (analysis_response['status'] == 0) {
            if (!clear_map) {
                city_map();
                clear_map = true;
            }
        }
    }
    catch (e) { }
}

function set_price(analysis_response) {
    if (analysis_response['status'] == 2) {
        document.getElementById("sum").innerHTML = analysis_response['price']
        if (analysis_response['price'] != 'Окончательная цена по итогу поездки.') {
            setProperty(document.getElementById("sum"), 'display', 'block');
            //priceModel.price(parseInt(analysis_response['price'].split(' ')[0]))
        }
        else {
            setProperty(document.getElementById("sum"), 'display', 'none');
            //priceModel.price(0);
        }
    }
    else {
        setProperty(document.getElementById("sum"), 'display', 'none');
        //priceModel.price(0);
    }
}

function call_analysis() {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var analysis_response = JSON.parse(xhr.responseText)
            set_price(analysis_response)
            work_with_map(analysis_response)
        }
    }
    var from_field = document.getElementById("from_address")
    var to_field = document.getElementById("to_address_1")
    var data = {}
    if (from_address_selected) {
        data[from_field.id] = from_field.value
    }
    else {
        data[from_field.id] = ''
    }
    if (to_address_1_selected) {
        data[to_field.id] = to_field.value
    }
    else {
        data[to_field.id] = ''
    }
    post('/route-analysis', data, finish)
}

function generate_parse_data(field){
    var data = {}
    data['field'] = field.value
    var tmp_rand = Math.floor(Math.random() * (1000000000 + 1));
    if(field.id == "from_address"){
        last_from_response_id = tmp_rand;
    }
    if (field.id == "to_address_1") {
        last_to_1_response_id = tmp_rand;
    }
    data['response_id'] = tmp_rand
    return data
}

function set_bad_address(field) {
    if (field.id == "from_address") {
        setAlert("from_not_found_error")
        from_address_bad_value = field.value
    }
    if (field.id == "to_address_1") {
        setAlert("to_not_found_error")
        to_1_address_bad_value = field.value
    }
}

function clear_bad_address(field) {
    setProperty(document.getElementById("same_addresses_error"), 'display', 'none');
    setProperty(document.getElementById("not_uniq_error"), 'display', 'none');
    if (field.id == "from_address") {
        setProperty(document.getElementById("from_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("from_empty_error"), 'display', 'none');
    }
    if (field.id == "to_address_1") {
        setProperty(document.getElementById("to_not_found_error"), 'display', 'none');
        setProperty(document.getElementById("to_empty_error"), 'display', 'none');
    }
}

function send_final_request(field) {
    var data = generate_parse_data(field)
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var options = JSON.parse(xhr.responseText)['addresses']
            if (options.length == 0) {
                set_bad_address(field)
                try { $("#" + field.id).autocomplete('destroy') } catch (e) { }               
            }
            else {
                if (field.value.length != 0) {
                    field.value = options[0].split('/')[0];
                    if(options[0].split('/')[2]){
                        field.value += options[0].split('/')[2];
                    }
                    field.value = field.value.replace(' ,', ',')
                    //field.value = options[0].replace(' /Екатеринбург/', '');
                    set_address_selected(field)
                    set_field_last_focus_out_value(field)
                }
                if (document.getElementById('from_address').value ===
                document.getElementById("to_address_1").value &&
                document.getElementById("to_address_1").value != '') {
                    setAlert('same_addresses_error')
                    setProperty(document.getElementById("sum"), 'display', 'none');
                    //priceModel.price(0);
                }
                else {
                    call_analysis();
                }
                
            }
        }
    }
    post('/parse-address', data, finish)
}

function send_request(field) {
    var finish = function (xhr) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var options = JSON.parse(xhr.responseText)['addresses']
            options.forEach(function (opt, ind, ar) { ar[ind] = create_option_html(opt);})
            var response_id = JSON.parse(xhr.responseText)['response_id']
            if (((field.id == "from_address" && response_id == last_from_response_id) ||
                (field.id == "to_address_1" && response_id == last_to_1_response_id))
                && ($(":focus")[0].id === field.id)) {
                    $("#" + field.id).autocomplete({
                        source: options, minLength: 0,
                        focus: function (ev, ui) {
                            field.value = get_option_by_html(ui.item.value);
                            return false;
                        },
                        select: function (ev, ui) {
                            try {
                                //ui.item.value = ui.item.value.split('/')[0] + ui.item.value.split('/')[2];
                                ui.item.value = get_option_by_html(ui.item.value);
                                //if (ui.item.value.split(', ').length < 2) {
                                //    ui.item.value += ', ';
                                //}
                            }
                            catch (e) {;}
                            //ui.item.value = ui.item.value.replace(' /Екатеринбург/', '');//fix
                            set_address_selected(field)
                            setTimeout(function(){set_field_last_focus_out_value(field)}, 500)
                            setTimeout(function () {
                                if (document.getElementById('from_address').value ===
                                    document.getElementById("to_address_1").value &&
                                    document.getElementById("to_address_1").value != '') {
                                    setAlert('same_addresses_error')
                                    setProperty(document.getElementById("sum"), 'display', 'none');
                                    //priceModel.price(0);
                                }
                                else {
                                    call_analysis();
                                }
                            }, 500)
                            //alert(2);
                        }
                    }).data("ui-autocomplete")._renderItem = function (ul, item) {
                        return $("<li></li>")
                            .data("item.autocomplete", item)
                            .append("<a>" + item.label + "</a>")
                            .appendTo(ul);
                    };
                    $("#" + field.id).autocomplete('search', '')
            }
        }
    }
    var data = generate_parse_data(field)
    post('/parse-address', data, finish)
}

function init_search() {
    var field_change = function (field) {
        //if (field.value.substr(-1) == ' ') {
        //    return
        //}
        set_address_not_selected(field)
        clear_bad_address(field)
        //alert(field.value + " " + field.value.length.toString())
        if (field.value.length < 3) {
            try { $("#" + field.id).autocomplete('destroy') } catch (e) { }
            if (field.value.length === 0) {
                call_analysis()
            }
            //alert()
        }
        else {
            send_request(field)
        }
    }
    var focus_out = function (field) {
        //alert(field.id + " " + field.value)
        if (field.value.length < 3) {
            try { $("#" + field.id).autocomplete('destroy') } catch (e) { }
            return
        }
        if (field.value === get_field_bad_value(field)) {
            try { $("#" + field.id).autocomplete('destroy') } catch (e) { }
            set_bad_address(field)
            return
        }
        if (field.value === get_field_last_focus_out_value(field)) {
            return;
        }
        send_final_request(field)
    }
    var field_focus = function (field) {
        clear_bad_address(field)
    }

    var from_field = document.getElementById("from_address")
    from_field.oninput = function () { field_change(from_field) }
    from_field.onfocus = function(){ field_focus(from_field)}
    from_field.onblur = function () { setTimeout(function () { focus_out(from_field) }, 250) }
    var to_field = document.getElementById("to_address_1")
    to_field.oninput = function () { field_change(to_field) }
    to_field.onfocus = function () { field_focus(to_field) }
    to_field.onblur = function () { setTimeout(function () { focus_out(to_field) }, 250) }
    var submitButton = document.getElementById("submitButton")
    submitButton.onclick = function () { document.getElementById("newOrderForm").onsubmit() }
    var cities_select = document.getElementById("cities-select")
    selected_city = cities_select.options[cities_select.selectedIndex].text;
    cities_select.onchange = function () {
        setCity(cities_select.options[cities_select.selectedIndex].text);
        from_field.value = '';
        to_field.value = '';
        clear_map = true;
        reinit_vars();
        selected_city = cities_select.options[cities_select.selectedIndex].text;
    }
}

