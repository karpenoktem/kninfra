var collapsedHeaderHeight = 70;
var headerHeight = 400;
var headerCollapsed = true;
var expandHeader = true;

// Work around a bug in Safari in private mode: Storage doesn't work.
var supportsStorage = true;
try {
    localStorage.setItem('test', '');
    localStorage.removeItem('test');
    sessionStorage.setItem('test', '');
    sessionStorage.removeItem('test');
} catch (error) {
    console.warn('localStorage or sessionStorage not supported');
    supportsStorage = false;
}

function email(t, d, u) {
    var email = u + '@' + d + '.' + t;
    document.write('<a href="mailto:' + email + '">' + email + '</a>');
}

function leden_api(data, cb) {
    $.post(leden_api_url, {
        csrfmiddlewaretoken: csrf_token,
        data: JSON.stringify(data),
    }, cb, "json");
}

function entityChoiceField_set(id, objid) {
    leden_api({action: "entity_humanName_by_id",
                'id': objid}, function(data) {
        if(!data)
            return;
        $('#_'+id).val(data);
        $('#'+id).val(objid);
    });
}

function entityChoiceField_get(id) {
    return $('#_'+id).val();
}

function create_entityChoiceField(id, params) {
    if(!params) params = {};
    if(!params.input_type) params.input_type = 'text';
    var hiddenEl = $('#'+id);
    var visibleEl = $("<input />");
    visibleEl.attr('id', '_' + id);
    visibleEl.attr('type', params.input_type)
    visibleEl.attr('required', hiddenEl.attr('required'));
    hiddenEl.after(visibleEl);
    if(params.placeholder) {
        visibleEl.attr('placeholder', params.placeholder);
    }
    var myParams = {
        source: function(request, response) {
            leden_api({
                action: "entities_by_keyword",
                keyword: request.term,
                type: params.type}, function(data) {
                    response($.map(data, function(item) {
                        return {value: item[1], key: item[0]};
                    }));
                });
        },
        select: function(event, ui) {
            visibleEl.val(ui.item.value);
            hiddenEl.val(ui.item.key);
            if (params.select) {
                params.select(ui.item.value, ui.item.key);
            }
            if (hiddenEl.attr('required')) {
                visibleEl[0].setCustomValidity('');
            }
            return false;
        },
        minLength: 0
    };
    if(params.position) {
        myParams.position = params.position;
    }
    visibleEl.autocomplete(myParams).focus(function() {
        $(this).trigger('keydown.autocomplete');
    });
    console.log(id, hiddenEl.attr('required'));
    if (hiddenEl.attr('required')) {
      visibleEl[0].setCustomValidity('Geen entity ingevuld');
      visibleEl.on('input', function() {
          visibleEl[0].setCustomValidity('Geen entity ingevuld (bewerkt)');
      });
    }
}

function checkGiedoSync(goal) {
    leden_api({action: "get_last_synced"},
        function(data) {
            if(data < goal)
                setTimeout(function(){checkGiedoSync(goal)}, 1000);
            else
                $('#waitingOnGiedoSyncNotice').remove();
        });
}

function isMobile() {
    // use matchMedia if available
    return 'ontouchstart' in document.documentElement && (window.matchMedia ? window.matchMedia('(max-device-width: 800px)') : true);
}

function qr_popup(url, elem) {
    if (window.QRCode) {
        var x = $("#qr-popup").remove()
        if (!x.length) {
            x = $('<div id="qr-popup"></div>')
        }
        var cnv = $('<canvas width=200 height=200>')
        cnv.appendTo(x.empty())
        x.appendTo(elem.parentNode)
        QRCode.toCanvas(cnv[0], url, {width: 200})
    } else {
        // load QRCode from unpkg
        var s = document.createElement("script")
        s.setAttribute("src", "https://unpkg.com/qrcode@1.5.0/build/qrcode.js")
        s.setAttribute("integrity", "sha384-hviKJNnYw4mnQ7yyq3dNQJXvzMtC2LDqfqVD1fECghvfaduQeAhvhp88wmz8P0Tu")
        s.setAttribute("crossorigin", "anonymous")
        s.addEventListener("load", function() {
            qr_popup(url, elem)
        })
        document.body.appendChild(s)
    }
}

function add_qr_links() {
    // insert (QR) link on all whatsapp chat links
    $('a[href^="https://chat.whatsapp.com"]').each(function() {
        var link = this
        var qr = $('<a class="qr-link" href="#qr">QR</a>').insertAfter(link)
        qr.click(function(event) {
            qr_popup(link.href, qr[0])
            event.preventDefault()
            return false
        })
    })
}

$(document).ready(function() {
    // ScrollUp animation
    $("#scrollUp").click(function(event) {
        $('html, body').animate({scrollTop: 0}, 300);
        event.preventDefault();
        return false;
    });

    if (expandHeader && supportsStorage) {
        /* reduce flicker on page load by loading the page with the header collapsed
         * and expanding it with JS while scrolling to the right position */
        $(document.body).addClass('header-expanded');
        var headerFixedThreshold = headerHeight - collapsedHeaderHeight;

        // Skip to content after first view.
        if (sessionStorage['visited'] &&
            getComputedStyle(document.body).paddingTop == headerHeight + "px") {
            $(document.body).addClass('viewedBefore');
            // <html> for Firefox, <body> for other browsers
            document.documentElement.scrollTop = headerFixedThreshold;
            document.body.scrollTop = headerFixedThreshold;
        }

        function fixHeader() {
            var shouldBeCollapsed = $(window).scrollTop() > headerFixedThreshold;
            if (headerCollapsed !== shouldBeCollapsed) {
                // don't touch the DOM if that's not needed!
                headerCollapsed = shouldBeCollapsed;
                if (shouldBeCollapsed) {
                    $('#header').addClass('fixed');
                } else {
                    $('#header').removeClass('fixed');
                }
            }
        }
        // Menubar half-fixed
        if (! isMobile()) {
            $(window).scroll(fixHeader);
            fixHeader();
        }
    }

    if (supportsStorage) {
        sessionStorage['visited'] = 'true';
    }

    $('.toggle').each(function(i, toggle) {
        toggle = $(toggle);
        var btn = $('.toggle-button', toggle);
        btn.bind('click', function (e) {
            toggle.toggleClass('toggle-open');
            e.preventDefault();
            e.stopPropagation();
        });
    });

    $(document.body).bind('click', function (e) {
        var target = $(e.target);
        if (target.hasClass('toggle-window') ||
            target.parents('.toggle-window').length) return;
        $('.toggle').removeClass('toggle-open');
    });

    if (!window.SVGSVGElement) {
        $(document.documentElement).addClass('no-svg');
    }

    $('.tabs').each(function(i, tabBox) {
        $('.tabHead', tabBox).each(function(j, tabHeader) {
            tabHeader = $(tabHeader);
            var tabBody = $('#'+tabHeader.data('for'));
            if (tabHeader.hasClass('selected')) {
                tabBody.addClass('selected');
            }
            tabHeader.on('click', function() {
                var oldHeader = $('.tabHead.selected', tabBox);
                if (tabHeader.is(oldHeader)) return;
                oldHeader.removeClass('selected');
                tabHeader.addClass('selected');
                var oldBody = $('.tabBody.selected', tabBox);
                oldBody.removeClass('selected');
                tabBody.addClass('selected');
            });
        });
    });

    // language picker
    $('#langpicker').change(function(e) {
        e.target.form.submit();
    });

    add_qr_links()
});

// Implement rot13 for email obscurification
function rot13 (s) {
    return jQuery.map(s.split(''), function(_) {
        if (!_.match(/[A-Za-z]/)) return _;
        c = _.charCodeAt(0)>=96;
        k = (_.toLowerCase().charCodeAt(0) - 96 + 12) % 26 + 1;
        return String.fromCharCode(k + (c ? 96 : 64));
    }
    ).join('');
}

function unobfuscateEmail() {
    var emails = document.querySelectorAll('.email.obfuscated');
    for (var i=0; i<emails.length; i++) {
        var email = emails[i];
        var email_link = document.createElement('a');
        email_link.textContent = rot13(email.textContent);
        email_link.href = 'mailto:' + (email_link.textContent || email_link.innerText);
        email_link.setAttribute('class', 'email');
        email.parentNode.insertBefore(email_link, email);
        email.parentNode.removeChild(email);
    }
}
document.addEventListener('DOMContentLoaded', unobfuscateEmail);

// vim: et:sta:bs=2:sw=4:
