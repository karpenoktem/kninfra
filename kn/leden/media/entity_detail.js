'use strict';

function api_set_property(id, property, value) {
	if (value === null) return;
	leden_api({
			action: 'entity_set_property',
			id: id,
			property: property,
			value: value},
		function(data) {
			if(data.ok) window.location.reload();
			else alert(data.error);
		});
}
