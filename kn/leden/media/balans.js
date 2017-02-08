'use strict';

function balansInit() {
  // works for only one table
  var balans = document.querySelector('table.balans');
  var mainrows = balans.querySelectorAll('tbody');
  for (var i=0; i<mainrows.length; i++) {
    mainrows[i].addEventListener('click', function(e) {
      var mainrow = e.target;
      while (mainrow.nodeName.toLowerCase() !== 'tbody') {
        mainrow = mainrow.parentNode;
      }
      mainrow.classList.toggle('expand');
    });
  }
};

balansInit();
