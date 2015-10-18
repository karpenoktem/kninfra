function events_api(data, cb) {
        $.post(events_api_url, {
                    csrfmiddlewaretoken: csrf_token,
                    data: JSON.stringify(data),
                }, cb, "json");
}
