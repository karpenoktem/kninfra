'use strict';


function promptNewProperty(id, property, message, oldValue) {
	var value = prompt(message, oldValue);
	if (!value) return;
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
