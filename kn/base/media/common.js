function email(t, d, u) {
    var email = u + '@' + d + '.' + t;
    document.write('<a href="mailto:' + email + '">' + email + '</a>');
}

function leden_api(data, cb) {
    $.post(leden_api_url, {
        csrfmiddlewaretoken: csrf_token,
        data: JSON.stringify(data),
    }, cb, "json");
}

function entityChoiceField_set(id, objid) {
    leden_api({action: "entity_humanName_by_id",
                'id': objid}, function(data) {
        if(!data)
            return;
        $('#_'+id).val(data);
        $('#'+id).val(objid);
    });
}

function create_entityChoiceField(id, type) {
    $('#'+id).after("<input type='text' id='_"+id+"' />");
    $('#_'+id).autocomplete({
        source: function(request, response) {
            leden_api({
                action: "entities_by_keyword",
                keyword: request.term,
                type: type}, function(data) {
                    response($.map(data, function(item) {
                        return {label: item[1], value: item[0]};
                    }));
                });
        }, select: function(event, ui) {
            $("#_"+id).val(ui.item.label);
            $("#"+id).val(ui.item.value);
            return false;
        }, minLength: 0}).focus(function() {
            $(this).trigger('keydown.autocomplete');
        });
}

// vim: et:sta:bs=2:sw=4:
