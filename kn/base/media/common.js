var headerHeight = 400;
var collapsedHeaderHeight = 70;
var headerFixedThreshold = headerHeight - collapsedHeaderHeight;

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
    $('#'+id).after("<input type='"+params.input_type+"' id='_"+id+"' />");
    var box = $('#_'+id);
    if(params.placeholder) {
        box.attr('placeholder', params.placeholder);
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
            $("#_"+id).val(ui.item.value);
            $("#"+id).val(ui.item.key);
            if (params.select) {
                params.select(ui.item.value, ui.item.key);
            }
            return false;
        },
        minLength: 0
    };
    if(params.position) {
        myParams.position = params.position;
    }
    box.autocomplete(myParams).focus(function() {
        $(this).trigger('keydown.autocomplete');
    });
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

function getCsrftoken() {
    if ($.cookie('csrftoken')) {
        return $.cookie('csrftoken');
    } else {
        // http://stackoverflow.com/a/12502559/559350
        // generate 32 pseudo-random characters
        var csrftoken = '';
        for (var i=0; i<4; i++) {
            csrftoken += Math.random().toString(36).slice(2, 10);
        }
        // emulate default Django behavior
        // https://github.com/django/django/blob/master/django/middleware/csrf.py#L182
        $.cookie('csrftoken', csrftoken, {path: '/', expires: 7*52})
        return csrftoken;
    }
}

function isMobile() {
    // use matchMedia if available
    return 'ontouchstart' in document.documentElement && (window.matchMedia ? window.matchMedia('(max-device-width: 800px)') : true);
}

// Menubar half-fixed
if (! isMobile()) {
    $(window).scroll(function(e) {
        if($.cookie('collapseHeader') === 'y') {
            $('#header').css({
                position: 'fixed',
                top: -headerFixedThreshold
            });
        } else if($(window).scrollTop() > headerFixedThreshold) {
            $('#header').css({
                position: 'fixed',
                top: -headerFixedThreshold
            });
        } else {
            $('#header').css({
                position: 'absolute',
                top: 0
            });
        }
    });
}

$(document).ready(function() {
    // ScrollUp animation
    $("#scrollUp").click(function(event) {
        var sTop = 0;
        if(!isMobile && $.cookie('collapseHeader') != 'y') {
            sTop = headerFixedThreshold;
        }
        $('html, body').animate({scrollTop: sTop}, 300);
            event.preventDefault();
            return false;
    });

    // read menu state collapse state from cookie
    if($.cookie('collapseHeader') === 'y') {
        $('#header').css({
            position: 'fixed',
            top: -headerFixedThreshold
        });
        $('#content').css({
            top: collapsedHeaderHeight
        });
    }

    // Skip to content after first view
    if (sessionStorage['visited']) {
        $('html, body').animate({
            scrollTop: $('#content').offset().top - collapsedHeaderHeight
        }, 'fast');
    }
    sessionStorage['visited'] = 'true';


    if (!isMobile()) {
        $('#csrfmiddlewaretoken').val(getCsrftoken());

        $(document.getElementById('loginButtonLink')).bind('click', function (event) {
            var loginButton = $('#loginButton');
            loginButton.toggleClass('open');
            event.preventDefault();
            event.stopPropagation();
        });

        $(document.body).bind('click', function (event) {
            $('#loginButton').removeClass('open');
        });

        $('#loginWindow').bind('click', function (event) {
            event.stopPropagation();
        });
    }
});

function collapseHeader(img) {
    if($.cookie('collapseHeader') === 'y') {
        $.cookie('collapseHeader', 'n');
        img.src = 'img/up.png';

        $('#content').css({
            top: headerHeight
        });

        $('#header').css({
            height: headerHeight
        });

        if($(window).scrollTop() > headerFixedThreshold) {
            $('#header').css({
                position: 'fixed',
                top: -headerFixedThreshold
            });
        } else {
            $('#header').css({
                position: 'absolute',
                top: 0
            });
        }
    } else {
        $.cookie('collapseHeader', 'y');
        img.src = 'img/down.png';
        $('#header').css({
            position: 'fixed',
            top: -headerFixedThreshold
        });
        $('#content').css({
            top: collapsedHeaderHeight
        });
    }
}

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
        if (email.textContent) {
            email_link.textContent = rot13(email.textContent);
        } else { /* IE8 */
            email_link.innerText = rot13(email.innerText);
        }
        email_link.href = 'mailto:' + (email_link.textContent || email_link.innerText);
        email_link.setAttribute('class', 'email');
        email.parentNode.insertBefore(email_link, email);
        email.parentNode.removeChild(email);
    }
}
if (document.addEventListener) {
    document.addEventListener('DOMContentLoaded', unobfuscateEmail);
} else { /* IE8 */
    window.attachEvent('onload', unobfuscateEmail);
}

// vim: et:sta:bs=2:sw=4:
