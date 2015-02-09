'use strict';
(function(){
  function KNF(){
    this.showing_foto = false;
    this.foto_shown = null;
    this.fotos_fetched = false;
  }

  KNF.prototype.change_path = function(path) {
    // Clear out the old
    $('#fotos').empty();
    $('#kruimelpad').empty();
    // Update state
    this.path = path; // it is important we set path before changing location
    if (this.get_url_path() != path)
      location.href = "#" + path;
    this.fotos = [];
    this.displaying_all_fotos = false;
    this.foto_offset = 0;
    this.fotos_fetched = false;
    // Update kruimelpad
    var cur = null;
    $.each([null].concat(path.split('/')), function(k, component) {
      if (component === '')
        return;
      if (component !== null) {
        $('<li>/</li>').appendTo('#kruimelpad');
        if (component === '') {
          return;
        } else if (!cur) {
          cur = component;
        } else {
          cur += '/' + component;
        }
      }
      var our_cur;
      if (component === null)
        our_cur = '';
      else
        our_cur = cur;
      var li = $('<li></li>')
          .click(function() {
            this.change_path(our_cur);
            return false;
          }.bind(this))
          .appendTo('#kruimelpad');
      $('<a href="javascript:void(0)"></a>').text(
            component ? component : 'fotos').appendTo(li);
    }.bind(this));
    // Fetch new
    this.fetch_fotos();
  };

  KNF.prototype.display_more_fotos = function() {
    if (!this.fotos_fetched)
      return;
    var limit = Math.min(this.fotos.length, this.foto_offset + 4);
    for (; this.foto_offset < limit; this.foto_offset++) {
      (function(i){
        var c = this.fotos[i];
        var srcset = c.thumbnail + " 1x, " +
                     c.thumbnail2x + " 2x"; 
        var thumb = $(
          '<li>'+
             '<img /> '+
             '<br/></li>');
        $('> img', thumb)
            .attr('srcset', srcset)
            .attr('src', c.thumbnail);
        if (c.thumbnailSize)
          $('> img', thumb)
              .attr('width', c.thumbnailSize[0])
              .attr('height', c.thumbnailSize[1]);
        var title = c.title;
        if (!title && c.type == 'album')
          title = c.name;
        if (title)
          $('<span></span>').text(title).appendTo(thumb);
        if (c.type == 'album') {
          thumb.click(function(){
            this.change_path(c.path);
            return false;
          }.bind(this));
        }
        if (c.type == 'foto') {

          thumb.click(function(){
            this.show_foto(i);
            return false;
          }.bind(this));
        }
        thumb.appendTo('#fotos');
      }.bind(this))(this.foto_offset);
    }
    if (this.foto_offset == this.fotos.length)
      this.displaying_all_fotos = true;
    else
      setTimeout(this.on_scroll.bind(this), 0);
  };

  KNF.prototype.cache_url = function(cache, path) {
    return "/foto/" + cache + "/" + encodeURI(path);
  };

  KNF.prototype.fetch_fotos = function() {
    var old_path = this.path;
    this.api({action: 'list',
              path: this.path},
      function(data) {
        if(old_path != this.path) return;
        if(data.error) return alert(data.error);
        
        $.each(data.children, function(i, c) {
          c.thumbnail = this.cache_url('thumb', c.path);
          c.thumbnail2x = this.cache_url('thumb2x', c.path);
          if (c.type == 'foto') {
            c.full = this.cache_url('full', c.path);
            c.large = this.cache_url('large', c.path);
            c.large2x = this.cache_url('large2x', c.path);
          }
          this.fotos.push(c);
        }.bind(this));
        this.fotos_fetched = true;
        this.display_more_fotos();
        setTimeout(this.on_scroll.bind(this), 0);
      }.bind(this));
  };

  KNF.prototype.on_scroll = function() {
    if (this.displaying_all_fotos || !this.fotos_fetched)
      return;
    var diff = $(document).height()
                  - $(window).scrollTop()
                  - $(window).height();
    if (diff >= 400)
      return;
    this.display_more_fotos();
  };

  // Returns the path according to the current URL
  KNF.prototype.get_url_path = function() {
    var tmp = location.hash;
    if (tmp.substr(0,1) == "#")
      tmp = tmp.substr(1);
    return tmp;
  };

  KNF.prototype.on_popstate = function() {
    var new_path = this.get_url_path();
    if (new_path == this.path)
      return;
    this.change_path(new_path);
  };

  KNF.prototype.api = function(data, cb) {
    $.post(fotos_api_url, {
      csrfmiddlewaretoken: csrf_token,
      data: JSON.stringify(data),
    }, cb, "json");
  };

  KNF.prototype.hide_foto = function() {
    this.showing_foto = false;
    $('#foto').hide();
    $('html').removeClass('noscroll');
  };

  KNF.prototype.change_foto = function(offset) {
    this.hide_foto();
    this.show_foto(offset);
  };

  KNF.prototype.show_foto = function(offset) {
    var foto = this.fotos[offset];
    this.showing_foto = true;
    this.foto_shown = offset;
    $('html').addClass('noscroll');
    var fotoDiv = $('#foto > div');
    fotoDiv.empty()
    var srcset = foto.large + " 1x, " +
                 foto.large2x + " 2x"; 
    var navHead = $('<div></div>').appendTo(fotoDiv);
    if (offset != 0)
      $('<a href="javascript:void(0)" class="prev">vorige</a>')
              .click(function(){this.change_foto(offset - 1); return false;}.bind(this))
              .appendTo(navHead);
    $('<span></span>')
              .text(foto.title ? foto.title : foto.name)
              .appendTo(navHead);
    if (offset != this.fotos.length - 1)
      $('<a href="javascript:void(0)" class="next">volgende</a>')
              .click(function(){this.change_foto(offset + 1); return false;}.bind(this))
              .appendTo(navHead);
    var img = $('<img/>')
            .attr('srcset', srcset)
            .attr('src', foto.large);
    if (foto.largeSize)
      img.attr('width', foto.largeSize[0])
         .attr('height', foto.largeSize[1]);
    img.appendTo(fotoDiv);
    var navFooter = $('<div></div>')
              .appendTo(fotoDiv);
    $('<a class="orig">origineel</a>')
            .attr('href', foto.full)
            .appendTo(navFooter);
    $('<div class="clear"></div>').appendTo(navFooter);
    if (foto.description)
      $('<p></p>')
            .text('foto.description')
            .appendTo(navFooter);
    $('#foto').show();
  };

  KNF.prototype.run = function() {
    this.on_popstate();
    $(window).scroll(this.on_scroll.bind(this));
    $(window).bind('popstate', this.on_popstate.bind(this));
    $('#foto').click(function(){
      this.hide_foto();
      return false;
    }.bind(this));
    $(document).keydown(function(e) {
      if (!this.showing_foto)
        return;
      // Escape
      if (e.which == 27) {
        this.hide_foto();
        return false;
      }
      // Left and right arrows
      if (e.which != 37 && e.which != 39)
        return;
      var offset = this.foto_shown;
      offset += e.which == 37 ? -1 : 1;
      if (offset < 0 || offset >= this.fotos.length)
        return;
      this.change_foto(offset);
      return false;
    }.bind(this));
  };

  $(document).ready(function(){
    (new KNF()).run();
  });
})();

/* vim: set et sta bs=2 sw=2 : */
