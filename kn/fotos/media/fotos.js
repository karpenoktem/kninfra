
var SWITCH_DURATION = 200; // 200ms, keep up to date with fotos.css

'use strict';
(function(){
  // Same as encodeURIComponent, but does not escape '/'.  Looks prettier.
  function encodePath(s) {
    return encodeURIComponent(s).replace(/(%)?%2f/gi,
        function($0, $1) { return $1 ? $0 : '/'; }); // No neg. lookbehind :-(
  }

  function mod(m, n) {
    // real modulo
    return ((m % n) + n) % n;
  }

  function Foto(data) {
    for (var k in data) {
      this[k] = data[k];
    }
    if (!this.tags) {
      this.tags = [];
    }

    this.calculate_cache_urls();
  };

  Foto.prototype.calculate_cache_urls = function() {
    var query = '?rot=' + this.rotation;
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
    return fotos_cache_root.replace('cachetype', cache) + encodePath(path);
  };

  Foto.prototype.anchor = function() {
    if ('relpath' in this) {
      // search result
      return this.relpath;
    }
    // normal photo
    return this.name;
  }


  function KNF(data){
    this.search_query = '';
    this.search_timeout = null;
    this.search_results = null;
    this.sidebar = false;
    this.saving_status = 0; /* enum: none, saved, saving, saving+queue */
    this.path = null;
    this.foto = null;
    this.fotos = {};
    this.parents = {};
    this.people = {};
    this.allpeople = [];
    this.swype_start = null;
    this.swype_moved = null;
    this.zoom_distance = null; // pinch-zoom action
    this.zoom_center = null;   // pinch-zoom action
    this.zoom_current = null;  // pinch-zoom action
    this.zoom_previous = null; // zoom session
    this.zoom_pan = null;      // pan action
    this.read_fotos(this.get_url_path(), data);
    this.nav_timeout = null;
    this.init_foto_frame();
  };

  KNF.prototype.change_path = function(path, query, keep_url) {
    query = query || '';

    // Clear out the old
    $('#fotos').empty();

    // Update path
    this.path = path;
    if (query !== this.search_query) {
      this.search_query = query;
      $('#search').val(this.search_query);
    }

    if (!keep_url) {
      this.apply_url(false);
    }

    this.update_breadcrumbs();
    if(this.path === '') {
      $('body').addClass('isroot');
    } else {
      $('body').removeClass('isroot');
    }

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

    if (this.search_query) {
      this.api({action: 'search',
                path: this.path,
                q: query},
        function(data) {
          if (this.search_query !== query) return;
          if (data.error) {
            alert(data.error);
            return;
          }
          this.search_results = {};
          var prev = null;
          for (var i=0; i<data.results.length; i++) {
            var foto = new Foto(data.results[i]);
            if (foto.type != 'album') {
              if (prev !== null) {
                prev.next = foto;
                foto.prev = prev;
              }
              prev = foto;
            }
            foto.relpath = foto.path.substr(
                this.path.length !== 0 ? this.path.length + 1 : 0);
            this.search_results[foto.relpath] = foto;
          }
          $.extend(this.people, data.people);
          this.display_fotos();
        }.bind(this));
    } else if (!(path in this.fotos)) {
      // Fetch fotos
      this.fetch_fotos();
    } else {
      this.display_fotos();
    }
  };

  KNF.prototype.update_breadcrumbs = function() {
    // Update breadcrumbs
    var breadcrumbs = $('#breadcrumbs');
    breadcrumbs.empty();
    var cur = '';
    $.each((this.path ? '/'+this.path : '').split('/'), function(k, component) {
      if (component !== '') {
        breadcrumbs.append(document.createTextNode(' / '));
        if (!cur) {
          cur = component;
        } else {
          cur += '/' + component;
        }
      }

      var a = $('<a></a>').text(
          this.parents[cur] || component).appendTo(breadcrumbs);
      var p = cur;
      a.attr('href', fotos_root+encodePath(cur))
       .click(function(e) {
        if (e.ctrlKey || e.shiftKey || e.metaKey || e.button != 0) {
          return;
        }
        this.change_path(p);
        return false;
      }.bind(this))
    }.bind(this));

    if (this.search_query) {
      breadcrumbs
        .append(document.createTextNode(' / '))
        .append($('<span>zoekresultaten</span>'));
    }
  }

  KNF.prototype.display_fotos = function() {
    if (!this.fotos[this.path])
      return;

    var field_visibility = $('#album-visibility');
    if (field_visibility) {
      field_visibility.val(this.fotos[this.path].visibility);
    }

    var fotos = [];
    if (this.search_query) {
      fotos = this.search_results;
    } else {
      fotos = this.fotos[this.path].children;
    }

    for (var name in fotos) {
      (function(c) {
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
            .attr('href', fotos_root + encodePath(c.path))
            .click(function(e) {
              if (e.ctrlKey || e.shiftKey || e.metaKey || e.button != 0) {
                return;
              }
              this.change_path(c.path);
              return false;
            }.bind(this));
        } else {
          $('a', thumb).attr('href', '#'+encodePath(c.anchor()));
        }
        thumb.addClass('visibility-' + c.visibility);
        thumb.appendTo('#fotos');
      }).call(this, fotos[name]);
    }

    $(window).lazyLoadXT();

    if (this.get_hash() && this.foto === null) {
      this.onhashchange();
    }
  };

  KNF.prototype.refresh_fotos = function() {
    $('#fotos').empty();
    this.display_fotos();
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
      album.people.push(name);
    }
    album.people.sort();
    $.extend(this.people, data.people);
  };

  KNF.prototype.read_people = function(people) {
    for (var i=0; i<people.length; i++) {
      this.people[people[i][0]] = people[i][1];
      this.allpeople.push(people[i][0]);
    }
  };

  KNF.prototype.apply_url = function (replace) {
    var url = fotos_root + encodePath(this.path);
    if (this.search_query) {
      url += '?q=' + encodeURIComponent(this.search_query);
    }
    if (this.foto) {
      url += '#' + this.foto.name;
    }
    if (!('pushState' in history)) {
      // Downwards compatibility with old browsers, primarily IE9.
      location.href = url;
    } else if (replace) {
      history.replaceState(null, '', url);
    } else {
      history.pushState(null, '', url);
    }
  };

  // Returns the path according to the current URL
  KNF.prototype.get_url_path = function() {
    // The indexOf is there so /nl/fotos/ has the same effect as /fotos/ (as
    // the URL /nl/fotos also gets the URL /fotos/ for fotos_root).
    return decodeURI(location.pathname.substr(
          location.pathname.indexOf(fotos_root)+fotos_root.length));
  };

  KNF.prototype.get_search_query = function() {
    // Read search query from URL
    // http://stackoverflow.com/a/901144/559350
    var results = (new RegExp("[\\?&]q=([^&#]*)")).exec(location.search);
    if (results !== null) {
      return decodeURIComponent(results[1].replace(/\+/g, " ")).trim();
    }
    return '';
  };

  KNF.prototype.onpopstate = function() {
    var path = this.get_url_path();
    var query = this.get_search_query();
    if (path === this.path && query === this.search_query)
      return;
    this.change_path(path, query, true);
  };

  // Returns the current photo name
  KNF.prototype.get_hash = function() {
    var hash = location.hash;
    if (hash.length < 1) {
      return '';
    }

    return decodeURIComponent(hash.substr(1));
  };

  KNF.prototype.onhashchange = function() {
    var name = this.get_hash();
    if (this.search_query) {
      var foto = this.search_results[name];
    } else {
      var foto = this.fotos[this.path].children[name];
    }
    this.change_foto(foto);
  };

  KNF.prototype.api = function(data, cb) {
    $.post(fotos_api_url, {
      csrfmiddlewaretoken: csrf_token,
      data: JSON.stringify(data),
    }, cb, "json");
  };

  KNF.prototype.change_foto = function(foto, confirmed) {
    // check for unsaved changes
    if (this.saving_status >= 2 && !confirmed) {
      console.warn('waiting until changes are saved');
      // Usually changes are saved within 100ms, so wait that time and try
      // again.
      setTimeout(function() {
        if (this.saving_status < 2) {
          this.change_foto(foto);
        } else if (confirm('Wijzigingen zijn niet opgeslagen.\nDoorgaan?')) {
          this.change_foto(foto, true);
        }
      }.bind(this), 100);
      return;
    }

    foto = foto || null;
    if (foto && foto.type != 'foto') {
      foto = null;
    }

    var frame = $('#foto');

    if (!foto) {
      // close photo frame if there is one
      if (this.foto) {
        frame.css('display', 'none'); // hide
        $('html').removeClass('noscroll');
        delete this.foto.newTags;
        this.foto = null;
      }
      $('.images', frame).empty();
      this.apply_url(false);
      return;
    }

    var direction = '';
    var reverseDirection= '';
    if (this.foto === foto.prev) {
      direction = 'right';
      reverseDirection = 'left';
    } else if (this.foto === foto.next) {
      direction = 'left';
      reverseDirection = 'right';
    }

    // Remove previous image
    var prev = $('#foto .images img[state=prev]');
    var current = $('#foto .images img[state=current]');
    var next = $('#foto .images img[state=next]');
    if (prev.length) {
      prev.remove();
      prev = null;
    }
    current.addClass(reverseDirection);
    current.attr('state', 'prev');
    prev = current;
    current = next;

    // Create the new photo - if swyping hasn't already created it.
    if (!current.length) {
      var current = $('<img class="img" state="current">');
      current.attr('data-name', foto.name);
      current.attr('src', this.chooseFoto(foto).src);
      if (direction) {
        current.addClass(direction);
        setTimeout(function() {
          // don't disturb dragging of the photo
          current.removeClass('settle');
        }.bind(this), SWITCH_DURATION);
      }
      $('.images', frame).append(current);
    }

    this.update_foto_frame(foto, direction);

    this.resize();
    $('html').addClass('noscroll');
    frame.css('display', 'flex'); // show

    if (direction) {
      // Force a reflow
      current.css('opacity');
      // Start the animation immediately (after the reflow).
      // Preferably this should be done in the 'loadstart' event, but that
      // sadly hasn't been implemented in browsers yet.
      current.addClass('settle');
      current.removeClass(direction);
    }
  };

  KNF.prototype.update_foto_frame = function(foto, direction) {
    console.log('updating to', foto.name);
    this.foto = foto;

    // Reset (clear) zoom action
    this.zoom_previous = null;
    this.zoom_current = null;
    this.zoom_distance = null;
    this.zoom_center = null;
    this.zoom_pan = null;

    var frame = $('#foto');

    $('.preload-image', frame).remove(); // remove old preloaders
    var preloadHref = null;
    if (direction == 'left' && foto.prev && foto.prev.type === 'foto') {
      // user will likely move to the left again
      preloadHref = this.chooseFoto(foto.prev).src;
    } else if (foto.next && foto.next.type === 'foto') {
      // user will likely move to the right again
      preloadHref = this.chooseFoto(foto.next).src;
    }
    if (preloadHref) {
      var preload = $('<link rel="preload" as="image" class="preload-image"/>');
      preload.attr('href', preloadHref);
      preload.on('load', function(e) {
        console.log('preload loaded:', e.target.href);
      });
      frame.append(preload);
    }

    // Update buttons, URL, title, etc.
    if (this.get_hash() != foto.anchor()) {
      this.apply_url(false);
    }
    $('.title', frame)
        .text(foto.title ? foto.title : foto.name);
    if (foto.prev && foto.prev.type != 'album')
      $('.prev', frame)
          .attr('href', '#'+encodePath(foto.prev.anchor()));
    else
      $('.prev', frame)
          .removeAttr('href');
    if (foto.next && foto.next.type != 'album')
      $('.next', frame)
          .attr('href', '#'+encodePath(foto.next.anchor()));
    else
      $('.next', frame)
          .removeAttr('href');
    $('.orig', frame)
        .attr('href', foto.full);
    $('.description', frame).text(foto.description || '');

    var sidebar = $('.sidebar', frame);
    $('input.title', sidebar)
        .val(this.foto.title)
        .attr('placeholder', this.foto.name);
    $('h2.title', sidebar)
        .text(this.foto.title || this.foto.name);
    $('.description', sidebar)
        .val(this.foto.description);
    $('select.visibility', sidebar)
        .val(this.foto.visibility);

    this.update_foto_tags(sidebar);
  };

  KNF.prototype.init_foto_frame = function() {
    var frame = $('#foto');
    $('.close', frame)
        .on('click', function() {
          this.change_foto(null);
          return false;
        }.bind(this));
    $('.open-sidebar', frame)
        .on('click', function(e) {
          if (this.sidebar) {
            this.close_sidebar();
          } else {
            this.open_sidebar();
          }
          return false;
        }.bind(this));

    var sidebar = $('.sidebar', frame);
    $('form', sidebar)
        .submit(function() {
          this.save_metadata();
          return false;
        }.bind(this));
    $('input.title', sidebar)
        .blur(function(e) {
          if (this.foto.title === e.target.value) return;
          this.save_metadata();
          return false;
        }.bind(this));
    $('textarea.description', sidebar)
        .blur(function(e) {
          if (this.foto.description === e.target.value) return;
          this.save_metadata();
          return false;
        }.bind(this));
    $('select', sidebar)
        .change(function(e) {
          if (this.foto.visibility === e.target.value) return;
          this.save_metadata();
          return false;
        }.bind(this));
    $('.remove', sidebar)
        .click(function(e) {
          this.removeFoto();
          return false;
        }.bind(this));
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

    function showhide() {
      if (this.nav_timeout === null) {
        frame.addClass('show-nav');
      } else {
        clearTimeout(this.nav_timeout);
      }
      this.nav_timeout = setTimeout(function() {
        this.nav_timeout = null;
        frame.removeClass('show-nav');
      }.bind(this), 1500);
    }
    frame.mousemove(showhide.bind(this));
    frame.on('touchstart', showhide.bind(this));

    frame.on('touchstart', this.touchstart.bind(this));
    frame.on('touchmove', this.touchmove.bind(this));
    frame.on('touchend', this.touchend.bind(this));
    frame.on('wheel', this.framewheel.bind(this));
  };

  KNF.prototype.touchstart = function (e) {
    if (this.sidebar) return;

    // Ignore the third (or more) finger
    if (e.originalEvent.touches.length > 2) return;

    // A second finger was placed on the surface
    if (e.originalEvent.touches.length == 2) {
      var prev = $('#foto .images img[state=prev]');
      if (prev.length) {
        // Possibly within a swype to the right. Let this image disappear to the left.
        var propsPrev = this.chooseFoto(this.foto.prev);
        prev.css('transform', 'translateX('+Math.min(0, -(this.maxWidth+propsPrev.width)/2) + 'px)')
        prev.addClass('settle');
        setTimeout(function() {
          prev.removeClass('settle');
          prev.css('transform', 'translateX(-9999px)');
        }, SWITCH_DURATION);
      }

      var next = $('#foto .images img[state=next]');
      if (next.length) {
        // Possibly within a swype to the left. Fade the next image.
        next.css({
          'transform': 'scale(0.5)',
          'opacity':   0,
        });
        next.addClass('settle');
        setTimeout(function() {
          next.removeClass('settle');
          next.css('transform', 'translateX(9999px)');
        }, SWITCH_DURATION);
      }

      if (this.zoom_pan !== null) {
        // We were panning, but now placing a 2nd finger on the surface.
        this.zoom_pan = null;
        if (this.zoom_current !== null) {
          this.zoom_previous = this.zoom_current;
          this.zoom_current = null;
        }
      }

      // TODO: code duplication
      var points = [{
        x: e.originalEvent.touches[0].clientX,
        y: e.originalEvent.touches[0].clientY,
      }, {
        x: e.originalEvent.touches[1].clientX,
        y: e.originalEvent.touches[1].clientY,
      }];
      var width = Math.abs(points[0].x - points[1].x);
      var height = Math.abs(points[0].y - points[1].y);
      // Distance between the two fingers (Pythagorean theorem)
      // Use the changed distance to calculate the scale (zoom) and the center
      // to calculate the movement.
      this.zoom_distance = Math.sqrt(width*width + height*height);
      // center between the fingers
      this.zoom_center = {
        x1: (points[0].x+points[1].x)/2,
        y1: (points[0].y+points[1].y)/2,
      };
      // center between the fingers after move - currently the same.
      this.zoom_center.x2 = this.zoom_center.x1;
      this.zoom_center.y2 = this.zoom_center.y1;

      if (this.zoom_previous === null) {
        // Start a pinch-zoom session: this is the first time two are together
        // on a surface since a switch/unzoom
        this.zoom_previous = {
          translateX: 0,
          translateY: 0,
          scale: 1,
        };
        // assume the first finger is points[0]
        var moved = points[0].x - this.swype_start;
        this.swype_start = null;
        if (moved < 0) {
          this.zoom_previous.translateX = moved;
          console.log('extra translateX', this.zoom_previous.translateX);
        }
        console.log('created zoom session', this.zoom_previous);
      }
    } else {
      // The first finger was placed on the surface
      if (this.zoom_previous === null) {
        this.swype_start = e.originalEvent.touches[0].clientX;
        console.log('swype start', this.swype_start);
      }
    }
  };

  KNF.prototype.touchmove = function(e) {
    if (this.sidebar) return;
    if (this.swype_start === null && this.zoom_previous === null) return;

    e.preventDefault();

    // Inside a pinch-zoom operation
    if (e.originalEvent.touches.length > 1) {
      // TODO: code duplication
      var points = [{
        x: e.originalEvent.touches[0].clientX,
        y: e.originalEvent.touches[0].clientY,
      }, {
        x: e.originalEvent.touches[1].clientX,
        y: e.originalEvent.touches[1].clientY,
      }];
      var width = Math.abs(points[0].x - points[1].x);
      var height = Math.abs(points[0].y - points[1].y);
      // Distance between the two fingers (Pythagorean theorem)
      // Use the changed distance to calculate the scale (zoom) and the center
      // to calculate the movement.
      var distance = Math.sqrt(width*width + height*height);
      this.zoom_center.x2 = (points[0].x+points[1].x)/2;
      this.zoom_center.y2 = (points[0].y+points[1].y)/2;
      var translateX = this.zoom_center.x2-this.zoom_center.x1;
      var translateY = this.zoom_center.y2-this.zoom_center.y1;
      var scale = distance / this.zoom_distance;
      this.zoom_current = {
        translateX: this.zoom_previous.translateX + translateX,
        translateY: this.zoom_previous.translateY + translateY,
        scale: this.zoom_previous.scale * scale,
      };
      // Add the fact that we're not zooming in the middle but possibly
      // somewhere on the edge, so the position should be adjusted.
      // If we didn't do anything, the center of the zoom would always be the
      // middle of the image.
      // So what are we doing here?
      // 1. Calculate the distance between the zoom_previous image center
      //    (screen center + translation) and the previous touch center.
      // 2. Scale this distance to what would be the current zoom center.
      // 3. Subtract the distance of (1) so we get the distance between the
      //    centers of zoom_previous and zoom_current.
      // 4. Add this distance to the zoom_current translation.
      var middlePointDistanceX = (this.zoom_previous.translateX + this.maxWidth/2 - this.zoom_center.x1);
      this.zoom_current.translateX +=  middlePointDistanceX * scale - middlePointDistanceX;
      var middlePointDistanceY = (this.zoom_previous.translateY + this.maxHeight/2 - this.zoom_center.y1);
      this.zoom_current.translateY +=  middlePointDistanceY * scale - middlePointDistanceY;

      this.apply_transform(this.zoom_current, false);
      return;
    }

    // Move photo while zoomed - only a single finger is used now
    if (this.zoom_previous !== null) {
      var point = {
        x: e.originalEvent.touches[0].clientX,
        y: e.originalEvent.touches[0].clientY,
      };
      if (this.zoom_pan === null) {
        this.zoom_pan = point;
      } else {
        var translateX = point.x - this.zoom_pan.x;
        var translateY = point.y - this.zoom_pan.y;
        this.zoom_current = {
          translateX: this.zoom_previous.translateX + translateX,
          translateY: this.zoom_previous.translateY + translateY,
          scale: this.zoom_previous.scale,
        };
        var current = $('#foto .images img[state=current]');
        current.css('transform', 'translate(' + this.zoom_current.translateX + 'px, ' + this.zoom_current.translateY + 'px) scale(' + this.zoom_current.scale + ')');
      }
      return;
    }

    // We're within a swype action (to the left or right).

    var moved = (e.originalEvent.touches[0].clientX - this.swype_start);
    if (moved > 0 && (!this.foto.prev || this.foto.prev.type === 'album')) {
      // first photo
      moved = 0;
    }
    if (moved < 0 && (!this.foto.next || this.foto.next.type === 'album')) {
      // last photo
      moved = 0;
    }

    this.swype_moved = moved;

    var current = $('#foto .images img[state=current]');
    var prev = $('#foto .images img[state=prev]'); // possibly 0
    var next = $('#foto .images img[state=next]'); // possibly 0

    if (moved < 0) {
      // Preview next image
      if (next.length == 0) {
        next = $('<img class="img" state="next"/>');
        next.attr('data-name', this.foto.next.name);
        next.attr('src', this.chooseFoto(this.foto.next).src);
        $('#foto .images').prepend(next);
        this.resize();
      }
      next.removeClass('settle'); // just in case
      next.css({
        'opacity':   Math.min(1, 1 - (this.maxWidth - -moved) / this.maxWidth),
        'transform': 'scale(' +Math.min(1, 1 - (this.maxWidth - -moved) / this.maxWidth / 2) + ')',
      });
      current.css({
        'transform': 'scale(1) translateX(' + moved + 'px)',
        'opacity':   1,
      });
    } else {
      next.css('opacity', 0);
    }

    if (moved > 0) {
      // Preview previous image
      var props = this.chooseFoto(this.foto.prev);
      if (prev.length == 0) {
        prev = $('<img class="img" state="prev"/>');
        prev.attr('data-name', this.foto.prev.name);
        prev.attr('src', props.src);
        $('#foto .images').append(prev);
        this.resize();
      }
      prev.removeClass('settle'); // just in case
      prev.css({
        'transform': 'translateX('+Math.min(0, moved - (this.maxWidth+props.width)/2) + 'px)',
        'opacity':   1,
      });
      current.css({
        'transform': 'scale('+Math.min(1, 1 - moved / this.maxWidth / 2)+')',
        'opacity':   Math.min(1, 1 - moved / this.maxWidth),
      });
    } else {
      prev.css('opacity', 0);
    }

    if (moved == 0) {
      current.css({
        'transform': '',
        'opacity':   1,
      });
    }
  };

  KNF.prototype.touchend = function(e) {
    if (this.sidebar) return;

    // ignore lifting the third (or more) finger
    if (e.originalEvent.touches.length > 1) return;

    // Lifting the 2nd finger
    if (e.originalEvent.touches.length == 1) {
      console.log('end of zoom - panning now', e.originalEvent.touches[0]);
      if (this.zoom_current !== null) {
        this.zoom_previous = this.zoom_current;
        this.zoom_current = null;
      }
      return;
    }

    if (this.zoom_previous !== null) {
      if (this.zoom_pan !== null) {
        // End of panning
        this.zoom_pan = null;
        if (this.zoom_current !== null) {
          this.zoom_previous = this.zoom_current;
          this.zoom_current = null;
        }
      }
      // Check for needed 'jump' at end of pinch zoom to center and zoom back
      // to 100% if needed
      var current = $('#foto .images img[state=current]');
      if (this.fix_zoom_end(this.zoom_center.x2, this.zoom_center.y2)) {
        console.log('end of zoom/pan gesture');
        this.apply_transform(this.zoom_previous, true);
      }

      return;
    }

    // We haven't moved yet - it's just a tap?
    if (this.swype_moved === null) return;

    // The swype action has ended. See whether we should switch the image or
    // just jump back to the current.

    var moved = this.swype_moved;
    this.swype_start = null;
    this.swype_moved = null;

    var current = $('#foto .images img[state=current]').last();
    var next = $('#foto .images img[state=next]'); // possibly 0
    var prev = $('#foto .images img[state=prev]'); // possibly 0

    if (moved < this.maxWidth / -16 && this.foto.next && this.foto.next.type != 'album') {
      // next image
      console.log('end of swype: next image');
      next.addClass('settle');
      next.css({
        'transform': '',
        'opacity':   1,
      });

      var props = this.chooseFoto(this.foto);
      current.css({
        'transform': 'translateX('+Math.min(0, -(this.maxWidth+props.width)/2) + 'px)',
        'opacity':   1,
      });
      current.addClass('settle');

      prev.remove();
      current.attr('state', 'prev');
      next.attr('state', 'current');
      setTimeout(function() {
        $('#foto .images img[state=prev]')
          .removeClass('settle')
          .css('transform', 'translateX(-9999px)');
        $('#foto .images img[state=current]')
          .removeClass('settle');
        // Create the next image (to cache)
        // not sure whether it actually helps...
        // TODO: code duplication
        if (this.foto.next && this.foto.next.type != 'album' &&
            $('#foto .images img[state=next]').length == 0) {
          var next = $('<img class="img" state="next">');
          next.attr('data-name', this.foto.next.name);
          next.css('transform', 'translateX(9999px)'); // off-screen
          next.attr('src', this.chooseFoto(this.foto.next).src);
          $('#foto .images').prepend(next);
          this.resize();
        }
      }.bind(this), SWITCH_DURATION);

      this.update_foto_frame(this.foto.next, 'right');

    } else if (moved > this.maxWidth / 16 && this.foto.prev && this.foto.prev.type != 'album') {
      // previous image
      console.log('end of swype: previous image');
      prev.css({
        'transform': '',
      });
      prev.addClass('settle');

      current.css({
        'transform': 'scale(0.5)',
        'opacity':   0,
      });
      current.addClass('settle');

      next.remove();
      current.attr('state', 'next');
      prev.attr('state', 'current');
      setTimeout(function() {
        $('#foto .images img[state=current]')
          .removeClass('settle');
        $('#foto .images img[state=next]')
          .removeClass('settle');
        // cache the previous image in case the user goes back one more
        // TODO: code duplication
        if (this.foto.prev && this.foto.prev.type != 'album' &&
            $('#foto .images img[state=prev]').length == 0) {
          var prev = $('<img class="img" state="prev">');
          prev.attr('data-name', this.foto.prev.name);
          prev.css('transform', 'translateX(-9999px)'); // off-screen
          prev.attr('src', this.chooseFoto(this.foto.prev).src);
          $('#foto .images').append(prev);
          this.resize();
        }
      }.bind(this), SWITCH_DURATION);

      this.update_foto_frame(this.foto.prev, 'left');

    } else {
      // current image
      console.log('end of swype: current image');
      current.css({
        'transform': '',
        'opacity':   1,
      });
      current.addClass('settle');

      next.css({
        'transform': 'scale(0.5)',
        'opacity':   0,
      });
      next.addClass('settle');

      prev.css({
        'transform': 'translateX('+(-this.maxWidth-8)+'px)',
      });
      prev.addClass('settle');

      setTimeout(function() {
        current.removeClass('settle');
        next.removeClass('settle');
        prev.removeClass('settle');
      }.bind(this), SWITCH_DURATION);
    }
  };

  KNF.prototype.framewheel = function(e) {
    var delta = e.originalEvent.deltaY;
    if (delta === 0) return;

    if (this.zoom_previous === null) {
      this.zoom_previous = {
        translateX: 0,
        translateY: 0,
        scale: 1,
      };
    }

    // There should be a better formula for this... but I can't think of one.
    var scale = 1.1;
    if (delta > 0) {
      var scale = Math.pow(scale, -1);
    }
    this.zoom_previous.scale *= scale;

    // Adjust the zoom center, just like in touchmove.
    var middlePointDistanceX = (this.zoom_previous.translateX + this.maxWidth/2 - e.originalEvent.clientX);
    this.zoom_previous.translateX +=  middlePointDistanceX * scale - middlePointDistanceX;
    var middlePointDistanceY = (this.zoom_previous.translateY + this.maxHeight/2 - e.originalEvent.clientY);
    this.zoom_previous.translateY +=  middlePointDistanceY * scale - middlePointDistanceY;

    this.fix_zoom_end(e.originalEvent.clientX, e.originalEvent.clientY);
    this.apply_transform(this.zoom_previous, false);
  };

  // Fixes things like the image shooting off the side or zooming with scale < 0
  KNF.prototype.fix_zoom_end = function(centerX, centerY) {
    if (this.zoom_previous.scale <= 1) {
      // Zoomed out - exit zoom/pan session (to enable back/forward swype)
      this.zoom_previous = null;
      return true;
    }

    // Still zoomed in - jump back to center if needed
    var props = this.chooseFoto(this.foto);
    var jump = {
      scale: Math.min(6, this.zoom_previous.scale),
      translateX: this.zoom_previous.translateX,
      translateY: this.zoom_previous.translateY,
    };

    // Adjust the zoom center, just like in touchmove.
    var middlePointDistanceX = (jump.translateX + this.maxWidth/2 - centerX);
    jump.translateX +=  middlePointDistanceX * (jump.scale/this.zoom_previous.scale) - middlePointDistanceX;
    var middlePointDistanceY = (jump.translateY + this.maxHeight/2 - centerY);
    jump.translateY +=  middlePointDistanceY * (jump.scale/this.zoom_previous.scale) - middlePointDistanceY;

    // Remove black borders - don't let the image move past the border of
    // the frame.
    var borderX = props.width/2*jump.scale - this.maxWidth/2;
    var borderY = props.height/2*jump.scale - this.maxHeight/2;
    jump.translateX = Math.max(-borderX, Math.min(borderX, jump.translateX));
    jump.translateY = Math.max(-borderY, Math.min(borderY, jump.translateY));

    // Jump to the center if the image is smaller than the frame.
    if (props.width * jump.scale <= this.maxWidth) {
      jump.translateX = 0;
    }
    if (props.height* jump.scale <= this.maxHeight) {
      jump.translateY = 0;
    }
    if (jump.scale != this.zoom_previous.scale ||
        jump.translateX != this.zoom_previous.translateX ||
        jump.translateY != this.zoom_previous.translateY) {
      // A jump is necessary.
      this.zoom_previous = jump;
      return true;
    }

    // No change
    return false;
  };

  KNF.prototype.apply_transform = function(zoom, animate) {
    var current = $('#foto .images img[state=current]');
    if (zoom === null) {
      current.css({
        transform: '',
        opacity:   1,
      });
    } else {
      current.css({
        transform: 'translate(' + zoom.translateX + 'px, ' + zoom.translateY + 'px) scale(' + zoom.scale + ')',
        opacity: 1,
      });
    }
    if (animate) {
      current.addClass('settle');
      setTimeout(function() {
        current.removeClass('settle');
      }, SWITCH_DURATION);
    }
  };

  KNF.prototype.update_foto_tags = function(sidebar) {
    var tagList = $('.tags', sidebar);
    tagList.empty();

    if (!('newTags' in this.foto)) {
      this.foto.newTags = this.foto.tags.slice(0); // clone
    }
    var newTags = this.foto.newTags;

    for (var i=0; i<newTags.length; i++) {
      var tag = newTags[i];
      var li = $('<li><a></a></li>');
      li.find('a')
        .text(this.people[tag])
        .attr('href', '/smoelen/gebruiker/' + tag + '/');
      tagList.append(li);
      if (fotos_admin) {
        $('<a class="remove">×</a>')
          .data('name', tag)
          .click(function(e) {
            var name = $(e.target).data('name');
            var index = newTags.indexOf(name);
            if (index < 0) {
              // ???
              return; // just to be sure
            }
            newTags.splice(index, 1);
            this.update_foto_tags(sidebar);
            this.save_metadata();
          }.bind(this))
          .appendTo(li);
      }
    }
    if (newTags.length == 0 && !fotos_admin) {
      tagList.html('<li><i>Geen tags</i></li>');
    }
    if (fotos_admin) {
      var people = [];
      var fotoPeople = {};
      var albumPeople = {};
      for (var i=0; i<newTags.length; i++) {
        fotoPeople[newTags[i]] = true;
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

      $('<li><input/></li>')
        .appendTo(tagList)
        .find('input')
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
            if (newTags.indexOf(name) >= 0) {
              // already in list
              return;
            }
            newTags.push(name);
            if (!(name in albumPeople)) {
              this.fotos[this.path].people.push(name);
            }
            this.update_foto_tags(sidebar);
            this.save_metadata();
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

  KNF.prototype.open_sidebar = function() {
    this.sidebar = true;
    $('#foto').addClass('sidebar');
    this.resize();
  };

  KNF.prototype.close_sidebar = function() {
    this.sidebar = false;
    $('#foto').removeClass('sidebar');
    this.resize();
  };

  KNF.prototype.removeFoto = function() {
    if (!confirm('Weet je zeker dat je deze foto wilt verwijderen?')) return;
    var foto = this.foto;
    this.api({action: 'remove',
              path: foto.path},
      function(data) {
        if (data.error) {
          alert(data.error);
          return;
        }
        // Foto successfully removed.
      });
    if (foto.prev) {
      foto.prev.next = foto.next;
    }
    if (foto.next) {
      foto.next.prev = foto.prev;
    }
    delete this.fotos[this.path].children[foto.name];
    this.change_foto(this.foto.next);
    this.refresh_fotos();
  };

  KNF.prototype.rotate = function(degrees) {
    if (!fotos_admin) return;
    if (!('oldRotation' in this.foto)) {
      this.foto.oldRotation = this.foto.rotation;
    }
    this.foto.rotation = mod(this.foto.rotation + degrees, 360);
    this.save_metadata();
  };

  KNF.prototype.save_metadata = function () {
    var sidebar = $('#foto .sidebar');
    var foto = this.foto;

    if (this.saving_status >= 2) {
      // Save again when the current save is done.
      this.saving_status = 3;
      return;
    }
    this.saving_status = 2;
    $('.status', sidebar).text('opslaan...');

    var field_title = $('.title', sidebar);
    var title = field_title.val();

    var field_description = $('.description', sidebar);
    var description = field_description.val();

    var field_visibility = $('.visibility', sidebar);
    var visibility = field_visibility.val();

    var tags = this.foto.tags;
    if ('newTags' in this.foto) {
      tags = this.foto.newTags;
    }

    this.api({action: 'set-metadata',
              path: foto.path,
              title: title,
              description: description,
              visibility: visibility,
              rotation: foto.rotation,
              tags: tags},
      function(data) {
        if (data.error) {
          // Should only happen when there's an issue with our API request.
          alert(data.error);
          return;
        }

        if (this.saving_status === 3) {
          this.saving_status = 1;
          this.save_metadata();
          return;
        }

        this.saving_status = 1;
        $('.status', sidebar).text('opgeslagen!');
        setTimeout(function() {
          if (this.saving_status !== 1) return;
          this.saving_status = 0;
          $('.status', sidebar).html('&nbsp;');
        }.bind(this), 1000);

        foto.thumbnailSize = data.thumbnailSize;
        foto.thumbnail2xSize = data.thumbnail2xSize;
        foto.largeSize = data.largeSize;
        foto.large2xSize = data.large2xSize;

        foto.description = description;
        foto.visibility = visibility;

        foto.calculate_cache_urls();
        if (foto === this.foto) {
          img.attr('src', this.chooseFoto(foto).src);
          this.resize();
        }

        foto.tags = tags;
        delete foto.newTags;

        if (title !== foto.title
            || 'oldRotation' in foto && foto.oldRotation !== foto.rotation) {
          foto.title = title;
          delete foto.oldRotation;
          this.refresh_fotos();
        }

        if (foto === this.foto) {
          var frame = $('#foto');
          $('.title', frame)
              .text(foto.title ? foto.title : foto.name);
          $('.description', frame)
              .text(foto.description);
        }
      }.bind(this));
  };

  KNF.prototype.updateMaxSize = function() {
    var wrapper = $('#foto .images');
    // The maxWidth/maxHeight property may be 0 when the frame isn't yet
    // visible.
    // window.outer* vars are a fallback (and the width is wrong when the
    // sidebar is visible on desktop), so only useful as a 'better than
    // nothing' value.
    this.maxWidth = wrapper.prop('clientWidth') || this.maxWidth
      || document.documentElement.clientWidth;
    this.maxHeight = wrapper.prop('clientHeight') || this.maxHeight
      || document.documentElement.clientHeight;
  };

  KNF.prototype.chooseFoto = function(foto) {
    var devicePixelRatio = 1.0;
    if ('devicePixelRatio' in window) {
      devicePixelRatio = window.devicePixelRatio;
    }

    var src = foto.large;
    var width = foto.largeSize[0];
    var height = foto.largeSize[1];
    if (width < this.maxWidth * devicePixelRatio &&
        height < this.maxHeight * devicePixelRatio) {
      if (foto.largeSize[0] != foto.large2xSize[0] ||
          foto.largeSize[1] != foto.large2xSize[1]) {
        src = foto.large2x;
        width = foto.large2xSize[0];
        height = foto.large2xSize[1];
      }
    }

    if (width > this.maxWidth) {
      height *= this.maxWidth/width;
      width  *= this.maxWidth/width;
    }
    if (height > this.maxHeight) {
      width  *= this.maxHeight/height;
      height *= this.maxHeight/height;
    }

    return {
      src: src,
      width: width,
      height: height,
    };
  };

  KNF.prototype.onresize = function() {
    this.updateMaxSize();
    this.resize();
  };

  KNF.prototype.resize = function() {
    $('#foto .images img').each(function(i, img) {
      img = $(img);
      console.log('updating', img.attr('data-name'));
      var foto = this.fotos[this.path].children[img.attr('data-name')];
      var props = this.chooseFoto(foto);
      img.css({'width': props.width,
               'height': props.height,
               'left': (this.maxWidth-props.width)/2,
               'top': (this.maxHeight-props.height)/2});
      // switch to 2x if needed (but don't switch back for this photo)
      if (props.src == this.foto.large2x &&
          img.attr('src') != this.foto.large2x) {
        img.attr('src', props.src);
      }
    }.bind(this));
  };

  KNF.prototype.onedit = function(e) {
    e.preventDefault();
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

  KNF.prototype.onhighlight = function() {
    $('html').toggleClass('fotos-highlight',
        $('#highlight').prop('checked'));
  };

  KNF.prototype.onsearch = function() {
    if (this.search_timeout !== null) {
      clearTimeout(this.search_timeout);
    }
    this.search_timeout = setTimeout(this.search.bind(this), 200);
  };

  KNF.prototype.search = function() {
    var oldsearch = this.search_query;
    this.search_query = $('#search').val().trim();
    if (oldsearch === this.search_query) {
      return;
    }
    this.change_path(this.path, this.search_query);
  };

  KNF.prototype.run = function() {
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
      if (e.target.nodeName === 'INPUT') {
        if (e.which == 27) { // Escape
          e.target.blur();
          return false;
        }
        if (e.target.value !== '') {
          // Don't handle keys when editing a textbox.
          return;
        }
      }
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
      // T (add tag)
      if (e.which == 84 && fotos_admin) {
        this.open_sidebar();
        $('#foto .tags input').focus();
        return false;
      }
    }.bind(this));

    $('#album-edit-button').click(this.onedit.bind(this));
    $('#highlight').on('change', this.onhighlight.bind(this));
    $('#search').on('input', this.onsearch.bind(this));
    $(window).resize(this.onresize.bind(this));

    var search = this.get_search_query();
    if (search) {
      $('#search').val(search);
    }

    this.updateMaxSize();
    this.onpopstate();
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
