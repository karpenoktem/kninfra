'use strict';
(function(){
  function mod(m, n) {
    // real modulo
    return ((m % n) + n) % n;
  }

  function Foto(data) {
    for (var k in data) {
      this[k] = data[k];
    }

    this.reload_cache_urls();
  };

  Foto.prototype.reload_cache_urls = function(query) {
    if (query === undefined) {
      query = '';
    }
    if (this.type == 'album') {
      if (this.thumbnailPath !== undefined) {
        this.thumbnail = this.cache_url('thumb', this.thumbnailPath) + query;
        this.thumbnail2x = this.cache_url('thumb2x', this.thumbnailPath) + query;
      }
    } else {
      this.thumbnail = this.cache_url('thumb', this.path) + query;
      this.thumbnail2x = this.cache_url('thumb2x', this.path) + query;
    }
    if (this.type == 'foto') {
      this.full = this.cache_url('full', this.path) + query;
      this.large = this.cache_url('large', this.path) + query;
      this.large2x = this.cache_url('large2x', this.path) + query;
    }
  };

  Foto.prototype.cache_url = function(cache, path) {
    return "/foto/" + cache + "/" + encodeURI(path);
  };


  function KNF(data){
    this.foto = null;
    this.sidebar = false;
    this.fotos = {};
    this.parents = {};
    this.people = {};
    this.allpeople = [];
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
    var album = {children:{},
                 visibility: data.visibility};
    this.fotos[path] = album;

    for (var k in data.parents) {
      this.parents[k] = data.parents[k];
    }

    if (!data.children) return;
    var prev = null;
    $.each(data.children, function(i, c) {
      c = new Foto(c);
      album.children[c.name] = c;

      if (prev !== null) {
        prev.next = c;
        c.prev = prev;
      }
      prev = c;

      if (c.type == 'album' && !(c.path in this.parents)) {
        this.parents[c.path] = c.title;
      }
    }.bind(this));

    album.people = [];
    for (var name in data.people) {
      this.people[name] = data.people[name];
      album.people.push(name);
    }
    album.people.sort();
  };

  KNF.prototype.read_people = function(people) {
    for (var i=0; i<people.length; i++) {
      this.people[people[i][0]] = people[i][1];
      this.allpeople.push(people[i][0]);
    }
  }

  KNF.prototype.pushState = function (path) {
    history.pushState(undefined, '', fotos_root + path);
  };

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
      delete this.foto.newRotation;
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
    $('.orig', frame)
        .attr('href', foto.full);
    if (foto.description)
      $('.description', frame).text(foto.description);

    $('.img', frame).on('load', this.onresize.bind(this));
    this.update_foto_src(foto);
    if (this.sidebar) {
      this.show_sidebar();
    }
    $('a.open-sidebar').click(function() {
      if (this.sidebar) {
        this.hide_sidebar();
      } else {
        this.show_sidebar();
      }
      return false;
    }.bind(this));

    $('#foto').show();
  };

  KNF.prototype.update_foto_src = function (foto) {
    var srcset = foto.large + " 1x, " +
                 foto.large2x + " 2x";
    $('#foto .img')
        .attr('srcset', srcset)
        .attr('src', foto.large);
  };

  KNF.prototype.show_sidebar = function() {
    this.sidebar = true;
    $('html').addClass('foto-sidebar');

    var sidebar = $('#foto .sidebar');
    $('.title', sidebar)
        .val(this.foto.title)
        .attr('placeholder', this.foto.name);
    if (this.foto.description)
      $('.description', sidebar)
          .val(this.foto.description);
    $('select.visibility', sidebar)
        .val(this.foto.visibility);

    this.update_foto_tags(sidebar);

    this.onresize();

    $('form', sidebar)
        .submit(function() {
          this.save_metadata();
          return false;
        }.bind(this));
    $('.save', sidebar)
        .submit(this.save_metadata.bind(this));
    $('a.rotate-left', sidebar)
        .click(function() {
          this.rotate(-90);
          return false;
        }.bind(this));
    $('a.rotate-right', sidebar)
        .click(function() {
          this.rotate(90);
          return false;
        }.bind(this));
  };

  KNF.prototype.update_foto_tags = function(sidebar) {
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
    if (fotos_admin) {
      var people = [];
      var fotoPeople = {};
      var albumPeople = {};
      for (var i=0; i<this.foto.tags.length; i++) {
        fotoPeople[this.foto.tags[i]] = true;
      }
      for (var i=0; i<this.fotos[this.path].people.length; i++) {
        var name = this.fotos[this.path].people[i];
        albumPeople[name] = true;
        if (name in fotoPeople) continue;
        people.push({label: this.people[name], value: name});
      }
      for (var i=0; i<this.allpeople.length; i++) {
        var name = this.allpeople[i];
        if (name in fotoPeople) continue;
        if (name in albumPeople) continue;
        people.push({label: this.people[name], value: name});
      }

      var newtag = $('<li><input/></li>')
        .appendTo(tags);
      newtag.find('input')
        .autocomplete({
          source: people,
          minLength: 0,
          autoFocus: true,
          delay: 0,
          select: function(e, ui){
            var name = ui.item.value;
            if (!(name in this.people)) {
              // none selected
              e.preventDefault();
              return;
            }
            for (var i=0; i<this.foto.tags.length; i++) {
              if (this.foto.tags[i] == name) return;
            }
            this.foto.tags.push(name);
            if (!(name in albumPeople)) {
              this.fotos[this.path].people.push(name);
            }
            $('#foto .save').prop('disabled', false);
            this.update_foto_tags(sidebar);
            sidebar.find('.tags input').focus();
          }.bind(this),
        })
        .keydown(function(e) {
          if (e.keyCode !== 13) return;
          if (e.target.value !== '' && !(e.target.value in this.people)) {
            // Workaround to not add the first person in the list while nothing
            // is in the input box.
            e.preventDefault();
          }
        }.bind(this));
    }
  };

  KNF.prototype.hide_sidebar = function() {
    this.sidebar = false;
    $('html').removeClass('foto-sidebar');
    this.onresize();
  };

  KNF.prototype.rotate = function(degrees) {
    if (!('newRotation' in this.foto)) {
      this.foto.newRotation = this.foto.rotation;
    }
    this.foto.newRotation = mod(this.foto.newRotation + degrees, 360);

    $('#foto .save').prop('disabled', false);
    this.onresize();
  };

  KNF.prototype.save_metadata = function () {
    var sidebar = $('#foto .sidebar');
    var foto = this.foto;

    var field_title = $('.title', sidebar);
    var title = field_title.val();
    field_title.prop('disabled', true);

    var field_description = $('.description', sidebar);
    var description = field_description.val();
    field_description.prop('disabled', true);

    var field_visibility = $('.visibility', sidebar);
    var visibility = field_visibility.val();
    field_visibility.prop('disabled', true);

    var rotation = this.foto.newRotation;
    if (rotation == undefined) {
      rotation = this.foto.rotation;
    }

    $('.tags input', sidebar).prop('disabled', true);

    this.api({action: 'set-metadata',
              path: foto.path,
              title: title,
              description: description,
              visibility: visibility,
              rotation: rotation,
              tags: foto.tags},
      function(data) {
        if (data.error) {
          alert(data.error);
          return;
        }

        foto.thumbnailSize = data.thumbnailSize;
        foto.largeSize = data.largeSize;

        field_title.prop('disabled', false);
        field_description.prop('disabled', false);
        field_visibility.prop('disabled', false);
        $('.tags input', sidebar).prop('disabled', false);

        foto.description = description;
        foto.visibility = visibility;

        var changed_rotation = rotation !== foto.rotation;
        foto.rotation = rotation;
        delete foto.newRotation;
        if (changed_rotation) {
          // invalidate cached cache urls
          foto.reload_cache_urls('?rotation='+foto.rotation);
          this.update_foto_src(foto);
        }

        if (title !== foto.title || changed_rotation) {
          foto.title = title;
          $('#fotos').empty();
          this.display_fotos();
        }

        if (this.sidebar && foto === this.foto) {
          var frame = $('#foto .foto-frame');
          $('.title', frame)
              .text(foto.title ? foto.title : foto.name);
          $('.description', frame)
              .text(foto.description);
          $('.save', frame)
              .prop('disabled', true);
        }
      }.bind(this));
  };


  KNF.prototype.onresize = function() {
    if (this.foto === null) return;

    var width = this.foto.largeSize[0];
    var height = this.foto.largeSize[1];

    var rotated = 'newRotation' in this.foto &&
        (this.foto.newRotation - this.foto.rotation) % 180 != 0;
    if (rotated) {
      // swap width and height
      var h = height;
      height = width;
      width = h;
    }

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
    // keep up to date with entities.py
    if (rotated && width > 850) {
      height *= 850/width;
      width  *= 850/width;
    }
    var margin = '';
    var transform = '';
    if ('newRotation' in this.foto &&
        this.foto.newRotation !== this.foto.rotation) {
      transform = 'rotate(' + mod(this.foto.newRotation - this.foto.rotation, 360) + 'deg)';
    }
    if (rotated) {
      var offset = (height-width)/2;
      margin = offset+'px ' + -offset+'px';
      var h = height;
      height = width;
      width = h;
    }
    $('#foto .img')
        .css({'width': width,
              'height': height,
              'margin': margin,
              'transform': transform});
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
      // [
      if (e.which == 219) {
        this.rotate(-90);
        return false;
      }
      // ]
      if (e.which == 221) {
        this.rotate(90);
        return false;
      }
    }.bind(this));

    $('#album-edit-button').click(this.onedit.bind(this));

    $(window).resize(this.onresize.bind(this));
  };

  $(document).ready(function(){
    var knf = new KNF(fotos);
    if (typeof fotos_people !== 'undefined') {
      knf.read_people(fotos_people);
    }
    knf.run();
  });
})();

/* vim: set et sta bs=2 sw=2 : */
