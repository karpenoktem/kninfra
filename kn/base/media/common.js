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

function entityChoiceField_get(id) {
    return $('#_'+id).val();
}

function create_entityChoiceField(id, params) {
    if(!params) params = {};
    if(!params.input_type) params.input_type = 'text';
    $('#'+id).after("<input type='"+params.input_type+"' id='_"+id+"' />");
    var box = $('#_'+id);
    if(params.placeholder) {
        box.attr('placeholder', params.placeholder);
    }
    if(params.attrs) {
        for(var attr in params.attrs) {
            if(attr == 'class') {
                box.addClass(params.attrs[attr]);
            } else if(box.attr(attr) == '') {
                box.attr(attr, params.attrs[attr]);
            }
        }
    }
    box.autocomplete({
        source: function(request, response) {
            leden_api({
                action: "entities_by_keyword",
                keyword: request.term,
                type: params.type}, function(data) {
                    response($.map(data, function(item) {
                        return {value: item[1], key: item[0]};
                    }));
                });
        }, select: function(event, ui) {
            $("#_"+id).val(ui.item.value);
            $("#"+id).val(ui.item.key);
            if (params.select)
                params.select(ui.item.value, ui.item.key);
            return false;
        }, minLength: 0}).focus(function() {
            $(this).trigger('keydown.autocomplete');
        });
}

function checkGiedoSync(goal) {
    leden_api({action: "get_last_synced"},
        function(data) {
            if(data < goal)
                setTimeout(function(){checkGiedoSync(goal)}, 1000);
            else
                $('#waitingOnGiedoSyncNotice').remove();
        });
}

// vim: et:sta:bs=2:sw=4:
