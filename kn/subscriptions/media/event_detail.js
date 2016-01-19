'use strict';

function _api(data, cb) {
    data.csrfmiddlewaretoken = csrf_token;
    $.post(events_api_url, data, cb, "json");
}

function event_set_opened(opened) {
    _api({'action': 'event-set-opened',
          'id': event_object_id,
          'opened': opened},
        function(d) {
            if(d.success) window.location.reload();
            if(d.error) alert(d.error);
    });
}

function close_event () {
    if(!confirm("Weet je zeker dat je de activiteit wilt sluiten?"))
        return;
    event_set_opened('false');
}

function reopen_event () {
    if(!confirm("Weet je zeker dat je de activiteit wilt heropenen? "))
        return;
    event_set_opened('true');
}

function copy_emailaddresses_to_clipboard () {
    event.preventDefault();
    _api({'action': 'get-email-addresses',
          'id': event_object_id},
        function(d) {
            if(d.error) {
                alert(d.error);
                return;
            }
            var s = '';
            var first = true;
            for(var i = 0; i < d.addresses.length; i++) {
                if (first) first = false;
                else s += ', ';
                s += d.addresses[i];
            }
            prompt("Dit zijn de e-mail adressen", s);
        });
}
