'use strict';

function api_set_property(id, property, value) {
	if (value === null) return;
	$.post(leden_api_url, {
			csrfmiddlewaretoken: csrf_token,
			data: JSON.stringify({
				action: 'entity_set_property',
				id: id,
				property: property,
				value: value})
		}, function(data) {
			if(data.ok) window.location.reload();
			else alert(data.error);
		});
}
