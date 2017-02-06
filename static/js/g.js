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
    ;
    Gabinet.prototype.showPdf = function (url, title, binary) {
        if (binary === void 0) { binary = false; }
        var width = $(document).width();
        if (width < 900)
            width = width - 30;
        else
            width = 870;
        var height = $(document).height() * 0.75;
        var save = '<button type="button" class="btn btn-primary">Save changes</button>';
        if (!binary)
            var pdf = "<object data=\"" + url + "\" type=\"application/pdf\" width=\"" + width + "\" height=\"" + height + "\">";
        else
            var pdf = "<embed data=\"data:application/pdf;base64," + url + "\" type=\"application/pdf\" width=\"" + width + "\" height=\"" + height + "\">\n            </embed>";
        if (!title)
            title = 'Dokument';
        this.showModal(title, pdf, save, 'modal-lg');
    };
    ;
    Gabinet.prototype.showModal = function (title, body, save, size) {
        if (size === void 0) { size = ''; }
        var modal = "<div id='pdf-modal' class=\"modal fade\">\n          <div class=\"modal-dialog " + size + "\" role=\"document\">\n            <div class=\"modal-content\">\n              <div class=\"modal-header\">\n                <h5 class=\"modal-title\">" + title + "</h5>\n                <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\">\n                  <span aria-hidden=\"true\">&times;</span>\n                </button>\n              </div>\n              <div class=\"modal-body\">\n                " + body + "\n              </div>\n              <div class=\"modal-footer\">\n                " + save + "\n                <button type=\"button\" class=\"btn btn-secondary\" data-dismiss=\"modal\">Zamknij</button>\n              </div>\n            </div>\n          </div>\n        </div>";
        $('#hidden').html(modal);
        $('#pdf-modal').modal({ show: true, keyboard: true });
    };
    ;
    Gabinet.prototype.showForm = function (form, params) {
        if (typeof (params) != "undefined") {
            var params_str = '?';
            for (p in params)
                params_str += p + '=' + params[p] + '&';
            params_str = params_str.substr(0, params_str.length - 2);
        }
        if (typeof (params) == "undefined")
            var url = "/static/forms/" + form;
        else
            var url = "/static/forms/" + form + "/" + params_str;
        this.showPdf(url);
    };
    ;
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