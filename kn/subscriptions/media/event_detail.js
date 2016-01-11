'use strict';

function _api(data, cb) {
    data.csrfmiddlewaretoken = csrf_token;
    $.post(events_api_url, data, cb, "json");
}

function close_event () {
    if(!confirm("Weet je zeker dat je de activiteit wilt sluiten? "+
                "Je kunt dit niet zelf ongedaan maken."))
        return;
    _api({'action': 'close-event',
          'id': event_object_id },
        function(d) {
            if(d.success) window.location.reload();
            if(d.error) alert(d.error);
    });
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
