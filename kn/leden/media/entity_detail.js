'use strict';


function call_api(el) {
  var actionString = el.dataset.action;
  var parts = actionString.split(':');
  var action = parts[0]; // e.g. 'entity_update_visibility'
  var key = parts[1];    // e.g. 'telephone'
  var value = parts[2];  // e.g. false

  // Value can be !confirm, ?prompt, or just a JSON value.
  if (value[0] == '!') {
    // confirm action
    if (!confirm(value.substr(1))) {
      return; // action aborted
    }
    value = null;
  } else if (value[0] == '?') {
    // request input
    var question = value.substr(1);
    var defaultValue = '';
    if (el.hasAttribute('data-default')) {
      defaultValue = el.getAttribute('data-default');
    } else if (el.hasAttribute('for')) {
      defaultValue = document.getElementById(el.getAttribute('for')).textContent;
    }
    value = prompt(question, defaultValue);
    if (value === null) {
      return; // action aborted
    }
  } else {
    value = JSON.parse(value);
  }

  $.post(leden_api_url,
    {
      csrfmiddlewaretoken: csrf_token,
      data: JSON.stringify({
        action: action,
        key:    key,
        value:  value,
        id:     object_id,
      }),
    }, function(data) {
      if (data.ok) {
        window.location.reload();
      } else {
        alert(data.error);
      }
    });
}

// Make sure every button will call the API.
(function() {
  var buttons = document.querySelectorAll('[data-action]');
  for (var i=0; i<buttons.length; i++) {
    let button = buttons[i];
    button.onclick = function(e) {
      call_api(e.target);
    };
  }
})()
