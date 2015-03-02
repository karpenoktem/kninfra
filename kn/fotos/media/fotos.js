'use strict';
(function(){
  function KNF(data){
    this.foto = null;
    this.sidebar = false;
    this.fotos = {};
    this.parents = {};
    this.people = {};
    this.read_fotos(this.get_url_path(), data);
  }

  KNF.prototype.change_path = function(path) {
    // Clear out the old
    $('#fotos').empty();
    // Update state
    this.path = path; // it is important we set path before changing location
    if (this.get_url_path() != path)
      this.pushState(path);

    this.update_breadcrumbs();

    // update album edit box
    var field_title = $('#album-title');
    if (field_title) {
      field_title.val(this.parents[this.path]);
      var parts = this.path.split('/');
      field_title.attr('placeholder', parts[parts.length-1]);
    }
    var field_visibility = $('#album-visibility');
    if (field_visibility) {
      field_visibility.val('');
    }

    if (!(path in this.fotos)) {
      // Fetch fotos
      this.fetch_fotos();
    } else {
      this.display_fotos();
    }
  };

  KNF.prototype.update_breadcrumbs = function() {
    // Update breadcrumbs
    $('#breadcrumbs').empty();
    var cur = '';
    $.each((this.path ? '/'+this.path : '').split('/'), function(k, component) {
      if (component !== '') {
        $('#breadcrumbs').append(document.createTextNode(' / '));
        if (!cur) {
          cur = component;
        } else {
          cur += '/' + component;
        }
      }

      var a = $('<a></a>').text(
          this.parents[cur] || component).appendTo('#breadcrumbs');
      var p = cur;
      a.attr('href', fotos_root+cur)
       .click(function(e) {
        if (e.ctrlKey || e.shiftKey || e.metaKey || e.button != 0) {
          return;
        }
        this.change_path(p);
        return false;
      }.bind(this))
    }.bind(this));
  }

  KNF.prototype.display_fotos = function() {
    if (!this.fotos[this.path])
      return;

    var field_visibility = $('#album-visibility');
    if (field_visibility) {
      field_visibility.val(this.fotos[this.path].visibility);
    }

    for (var name in this.fotos[this.path].children) {
      (function(name) {
        var c = this.fotos[this.path].children[name];
        var thumb = $('<li><div><a><img class="lazy" /></a></div></li>');
        if (c.thumbnail !== undefined) {
          var srcset = c.thumbnail + " 1x, " +
                       c.thumbnail2x + " 2x";
          $('img', thumb)
              .attr('data-srcset', srcset)
              .attr('data-src', c.thumbnail);
          if (c.thumbnailSize) {
            $('img', thumb)
                .attr('width', c.thumbnailSize[0])
                .attr('height', c.thumbnailSize[1]);
            // http://www.smashingmagazine.com/2013/09/16/responsive-images-performance-problem-case-study/
            $('a', thumb).css('padding-bottom', c.thumbnailSize[1]/c.thumbnailSize[0]*100+'%')
                         .css('width', c.thumbnailSize[0]);
            $('div', thumb).css('margin', '0 ' + (200-c.thumbnailSize[0])/2/200*100 + '%');
          }
        } else {
          $('a', thumb).text('(geen thumbnail)')
                       .css('height', '100px');
        }
        var title = c.title;
        if (!title && c.type == 'album')
          title = c.name;
        if (title)
          $('<span></span>').text(title).appendTo(thumb);
        if (c.type == 'album') {
          $('a', thumb)
            .attr('href', fotos_root + c.path)
            .click(function(e) {
              if (e.ctrlKey || e.shiftKey || e.metaKey || e.button != 0) {
                return;
              }
              this.change_path(c.path);
              return false;
            }.bind(this));
        }
        if (c.type == 'foto') {
          $('a', thumb).attr('href', '#'+c.name);
        }
        thumb.appendTo('#fotos');
      }).call(this, name);
    }

    $(window).lazyLoadXT();

    if (this.get_hash() && this.foto === null) {
      this.change_foto(this.fotos[this.path].children[this.get_hash()]);
    }
  };

  KNF.prototype.cache_url = function(cache, path) {
    return "/foto/" + cache + "/" + encodeURI(path);
  };

  KNF.prototype.fetch_fotos = function() {
    var path = this.path;
    if (this.fotos[path] === null) {
      // fetch in progress
      return;
    }
    this.fotos[path] = null;
    this.api({action: 'list',
              path: path},
      function(data) {
        if(data.error) {
          $('#fotos').text(data.error);
          return;
        }

        this.read_fotos(path, data);

        this.display_fotos();
      }.bind(this));
  };

  KNF.prototype.read_fotos = function(path, data) {
    this.fotos[path] = {children:{},
                        visibility: data.visibility};

    var prev = null;
    $.each(data.children, function(i, c) {
      if (c.type == 'album') {
        if (c.thumbnailPath !== undefined) {
          c.thumbnail = this.cache_url('thumb', c.thumbnailPath);
          c.thumbnail2x = this.cache_url('thumb2x', c.thumbnailPath);
        }
      } else {
        c.thumbnail = this.cache_url('thumb', c.path);
        c.thumbnail2x = this.cache_url('thumb2x', c.path);
      }
      if (c.type == 'foto') {
        c.full = this.cache_url('full', c.path);
        c.large = this.cache_url('large', c.path);
        c.large2x = this.cache_url('large2x', c.path);
      }
      this.fotos[path].children[c.name] = c;

      if (prev !== null) {
        prev.next = c;
        c.prev = prev;
      }
      prev = c;

      if (c.type == 'album' && !(c.path in this.parents)) {
        this.parents[c.path] = c.title;
      }
    }.bind(this));

    for (var k in data.parents) {
      this.parents[k] = data.parents[k];
    }

    for (var name in data.people) {
      this.people[name] = data.people[name];
    }
  }

  KNF.prototype.pushState = function (path) {
    history.pushState(undefined, '', fotos_root + path);
  }

  // Returns the path according to the current URL
  KNF.prototype.get_url_path = function() {
    return location.pathname.substr(fotos_root.length);
  };

  KNF.prototype.onpopstate = function() {
    var new_path = this.get_url_path();
    if (new_path === this.path)
      return;
    this.change_path(new_path);
  };

  // Returns the current photo name
  KNF.prototype.get_hash = function() {
    var hash = location.hash;
    if (hash.length < 1) {
      return '';
    }

    return hash.substr(1);
  }

  KNF.prototype.onhashchange = function() {
    this.change_foto(this.fotos[this.path].children[this.get_hash()]);
  }

  KNF.prototype.api = function(data, cb) {
    $.post(fotos_api_url, {
      csrfmiddlewaretoken: csrf_token,
      data: JSON.stringify(data),
    }, cb, "json");
  };

  KNF.prototype.change_foto = function(foto) {
    if (this.foto) {
      $('#foto').hide();
      $('#foto .foto-frame').remove();
      $('html').removeClass('noscroll');
    }
    foto = foto || null;
    this.foto = foto;
    if (!foto) {
      this.pushState(this.get_url_path());
      return;
    }
    if (this.get_hash() != foto.name) {
      location.hash = '#' + foto.name;
    }
    $('html').addClass('noscroll');
    var frame = $('.foto-frame.template').clone().removeClass('template');
    frame.appendTo('#foto');
    $('.title', frame)
        .text(foto.title ? foto.title : foto.name);
    if (foto.prev)
      $('.prev', frame)
          .attr('href', '#'+foto.prev.name);
    if (foto.next)
      $('.next', frame)
          .attr('href', '#'+foto.next.name);
    var srcset = foto.large + " 1x, " +
                 foto.large2x + " 2x";
    $('.img', frame)
        .attr('srcset', srcset)
        .attr('src', foto.large)
    $('.orig', frame)
        .attr('href', foto.full);
    if (foto.description)
      $('.description', frame).text(foto.description);

    $('a.open-sidebar').click(function() {
      if (this.sidebar) {
        this.hide_sidebar();
      } else {
        this.show_sidebar();
      }
      return false;
    }.bind(this));
    if (this.sidebar) {
      this.show_sidebar();
    }

    this.onresize();
    $('#foto').show();
  };

  KNF.prototype.show_sidebar = function() {
    this.sidebar = true;
    $('html').addClass('foto-sidebar');

    var sidebar = $('#foto .sidebar');
    $('.title', sidebar)
        .val(this.foto.title)
        .attr('placeholder', this.foto.name);
    $('select.visibility', sidebar)
        .val(this.foto.visibility);

    var tags = $('.tags', sidebar);
    tags.empty();
    for (var i=0; i<this.foto.tags.length; i++) {
      var tag = this.foto.tags[i];
      var li = $('<li><a></a></li>');
      li.find('a')
        .text(this.people[tag])
        .attr('href', '/smoelen/gebruiker/' + tag + '/');
      tags.append(li);
    }
    if (this.foto.tags.length == 0) {
      tags.html('<i>Geen tags</i>');
    }

    this.onresize();

    $('form', sidebar)
        .submit(function() {
          this.save_metadata();
          return false;
        }.bind(this));
    $('.save', sidebar)
        .submit(this.save_metadata.bind(this));
  }

  KNF.prototype.hide_sidebar = function() {
    this.sidebar = false;
    $('html').removeClass('foto-sidebar');
    this.onresize();
  }

  KNF.prototype.save_metadata = function () {
    var sidebar = $('#foto .sidebar');
    var foto = this.foto;

    var field_title = $('.title', sidebar)
    var title = field_title.val();
    field_title.prop('disabled', true);

    var field_visibility = $('.visibility', sidebar);
    var visibility = field_visibility.val();
    field_visibility.prop('disabled', true);

    this.api({action: 'set-metadata',
              path: foto.path,
              title: title,
              visibility: visibility},
      function(data) {
        if (data.error) {
          alert(data.error);
          return;
        }

        field_title.prop('disabled', false);
        field_visibility.prop('disabled', false);

        foto.visibility = visibility;

        if (title !== foto.title) {
          foto.title = title;
          $('#fotos').empty();
          this.display_fotos();
        }

        if (this.sidebar && foto === this.foto) {
          var frame = $('#foto .foto-frame');
          $('.title', frame)
              .text(foto.title ? foto.title : foto.name);
          $('.save', frame)
              .prop('disabled', true);
        }
      }.bind(this));
  };


  KNF.prototype.onresize = function() {
    if (this.foto === null) return;

    var width = this.foto.largeSize[0];
    var height = this.foto.largeSize[1];

    var maxWidth  = window.innerWidth;
    var maxHeight = window.innerHeight;
    // Keep up to date with stylesheet!
    if (maxWidth > 500) {
      maxWidth -= 10*2;
    }
    if (maxHeight > 800) {
      maxHeight -= 10*2 + 40*2 + (15+(6*2))*2;
    } else {
      maxHeight -= 5*2 + (15+(6*2))*2;
    }
    if (this.sidebar) {
      maxWidth -= 200;
    }
    if (width > maxWidth) {
        height *= maxWidth/width;
        width  *= maxWidth/width;
    }
    if (height > maxHeight) {
        width  *= maxHeight/height;
        height *= maxHeight/height;
    }
    $('#foto .img')
        .attr('width', width)
        .attr('height', height);
  };

  KNF.prototype.onedit = function(e) {
    e.target.disabled = true;

    var field_visibility = $('#album-visibility')
    field_visibility.prop('disabled', true);
    var visibility = field_visibility.val();

    var field_title = $('#album-title')
    field_title.prop('disabled', true);
    var title = field_title.val()

    var path = this.path;
    this.api({action: 'set-metadata',
              path: path,
              title: title,
              visibility: visibility},
      function(data) {
        if (data.error) {
          alert(data.error);
          return;
        }
        field_title.prop('disabled', false);
        field_visibility.prop('disabled', false);

        // update/clear cache
        this.parents[path] = title;
        if (path !== '') {
          var parts = path.split('/');
          delete this.fotos[parts.slice(0, parts.length-1).join('/')];
        }

        this.update_breadcrumbs();
      }.bind(this));
  };

  KNF.prototype.run = function() {
    this.onpopstate();
    $(window).bind('popstate', this.onpopstate.bind(this));
    $(window).bind('hashchange', this.onhashchange.bind(this));
    $('#foto').click(function(e) {
      if (e.target.id !== 'foto') return;
      this.change_foto(null);
      return false;
    }.bind(this));
    $(document).keydown(function(e) {
      if (!this.foto)
        return;
      // Escape
      if (e.which == 27) {
        this.change_foto(null);
        return false;
      }
      // left arrow
      if (e.which == 37) {
        this.change_foto(this.foto.prev);
        return false;
      }
      // right arrow
      if (e.which == 39) {
        this.change_foto(this.foto.next);
        return false;
      }
    }.bind(this));

    $('#album-edit-button').click(this.onedit.bind(this));

    $(window).resize(this.onresize.bind(this));
  };

  $(document).ready(function(){
    (new KNF(fotos)).run();
  });
})();

/* vim: set et sta bs=2 sw=2 : */
