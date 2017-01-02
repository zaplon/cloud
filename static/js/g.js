/// <reference path="types/jquery.d.ts" />
/// <reference path="types/bootstrap.d.ts" />
var Gabinet = (function () {
    function Gabinet() {
        this.pageLimit = 10;
    }
    ;
    Gabinet.prototype.logout = function () {
        $.post('/account/logout/', function () {
            window.location.href = '/';
        });
    };
    ;
    Gabinet.prototype.transformTableResponse = function (res) {
        return { total: res.count, rows: res.results };
    };
    ;
    Gabinet.prototype.settings = function () {
        $.get('/profile/settings/', function (res) {
            $('#hidden').append(res);
            $.getScript('/static/js/user_profile/settings.js', function () { ready(); });
            $('#settings-modal').modal({ show: true, keyboard: true });
        });
    };
    return Gabinet;
})();
var gabinet = new Gabinet();
$(document).ready(function () {
    $('#logout').click(gabinet.logout);
    $('#settings').click(gabinet.settings);
});
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
//# sourceMappingURL=g.js.map