'use strict';


function call_api(el) {
  var progress = el.parentNode.querySelector('.progress');
  var actionString = el.dataset.action;
  var parts = actionString.split(':');
  var action = parts[0]; // e.g. 'entity_update_visibility'
  var key = parts[1];    // e.g. 'telephone'
  if (el.type == 'checkbox') {
    var value = el.checked;
  } else {
    var value = parts[2]; // The value to send with the API request.
  }

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

  if (el.type == 'checkbox') { // inline feedback
    progress.textContent = 'Opslaan...'; // TODO: i18n
  }
  el.disabled = true;
  el.dataset.lastChange = (new Date()).getTime();
  var lastChange = el.dataset.lastChange;
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
      if (el.type == 'checkbox') {
        // can do inline feedback
        if (data.ok) {
          progress.textContent = 'Opgeslagen!'; // TODO: i18n
          el.disabled = false;
          setTimeout(function() {
            if (lastChange === el.dataset.lastChange) {
              progress.textContent = '';
            }
          }, 1000);
        } else {
          progress.textContent = data.error;
          el.disabled = false;
        }
      } else {
        // must do modal/full-page feedback
        if (data.ok) {
          window.location.reload();
        } else {
          alert(data.error);
        }
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
