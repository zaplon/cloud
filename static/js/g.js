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
    Gabinet.prototype.minimize = function (me, e) {
        var target = $(e.target).attr('data-target');
        $('#' + target).animate({ height: "toggle" });
    };
    ;
    Gabinet.prototype.fixData = function (data) {
        newData = [];
        for (d in data) {
            if (data[d].name.startsWith('factory_') && !($.isArray(data[d].value)))
                data[d].value = [data[d].value];
            var hits = newData.filter(function (n) { return n.name == data[d].name; });
            if (hits.length == 0)
                newData.push(data[d]);
            else {
                if ($.isArray(hits[0].value))
                    hits[0].value.push(data[d].value[0]);
                else
                    hits[0].value = [hits[0].value, data[d].value[0]];
            }
        }
        return JSON.stringify(newData);
    };
    ;
    Gabinet.prototype.settings = function () {
        $.get('/profile/settings/', function (res) {
            $('#settings-modal').remove();
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
    Gabinet.prototype.showModal = function (title, body, save, size, hideFooter) {
        if (size === void 0) { size = ''; }
        if (hideFooter === void 0) { hideFooter = false; }
        var modal = ("<div id='pdf-modal' class=\"modal fade\">\n          <div class=\"modal-dialog " + size + "\" role=\"document\">\n            <div class=\"modal-content\">\n              <div class=\"modal-header\">\n                <h5 class=\"modal-title\">" + title + "</h5>\n                <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\">\n                  <span aria-hidden=\"true\">&times;</span>\n                </button>\n              </div>\n              <div class=\"modal-body\">\n                " + body + "\n              </div>\n              ") + (hideFooter ? '' :
            "<div class=\"modal-footer\">\n                " + save + "\n                <button type=\"button\" class=\"btn btn-secondary\" data-dismiss=\"modal\">Zamknij</button>\n              </div>") +
            "</div>\n          </div>\n        </div>";
        $('#hidden').html(modal);
        $('#pdf-modal').modal({ show: true, keyboard: true });
    };
    ;
    Gabinet.prototype.showForm = function (form, params, html5) {
        if (typeof (params) != "undefined") {
            var params_str = '?';
            for (p in params)
                params_str += p + '=' + params[p] + '&';
            params_str = params_str.substr(0, params_str.length - 2);
        }
        if (html5) {
            var me = this;
            if (typeof (params) == "undefined")
                params = {};
            var name = form.split('.')[0];
            params.form = name;
            params.height = $(window).height() - 60 < 400 ? 400 : $(window).height() - 60;
            var url = "/forms/edit_form/";
            $.get(url, params, function (res) {
                me.showModal(form, res, '', 'modal-form', true);
                formViewModel.name = name;
                ko.applyBindings(formViewModel, $('#form-editor')[0]);
            });
        }
        else {
            if (typeof (params) == "undefined")
                var url = ("/static/forms/" + form) + new Date();
            else
                var url = ("/static/forms/" + form + "/" + params_str) + new Date();
            this.showPdf(url);
        }
    };
    ;
    Gabinet.prototype.addRecipes = function () {
        var body = $('#addRecipeForm').html();
        var save = '<button class="btn btn-primary" id="addRecipes">Dodaj</button>';
        gabinet.showModal('Dodaj numery recept', body, save);
        $('#addRecipes').click(function () {
            var file_data = $('.modal #recipeInputFile').prop('files')[0];
            if (!file_data) {
                $('.modal #recipe-errors').html('Musisz wybrać plik');
                return;
            }
            var form_data = new FormData();
            form_data.append('file', file_data);
            $.ajax({
                // Your server script to process the upload
                url: '/profile/add_recipes/',
                type: 'POST',
                // Form data
                data: form_data,
                // Tell jQuery not to process data or worry about content-type
                // You *must* include these options!
                cache: false,
                contentType: false,
                processData: false,
                success: function (res) {
                    if (res.success) {
                        $('button.close').click();
                    }
                    else {
                        $('.modal #recipe-errors').html(res.errors);
                    }
                },
                fail: function (res) {
                    $('.modal #recipe-errors').html('plik jest niepoprawny lub wystąpił błąd');
                },
                // Custom XMLHttpRequest
                xhr: function () {
                    var myXhr = $.ajaxSettings.xhr();
                    if (myXhr.upload) {
                        // For handling the progress of the upload
                        myXhr.upload.addEventListener('progress', function (e) {
                            if (e.lengthComputable) {
                                $('progress').attr({
                                    value: e.loaded,
                                    max: e.total
                                });
                            }
                        }, false);
                    }
                    return myXhr;
                }
            });
        });
    };
    ;
    return Gabinet;
})();
;
var gabinet = new Gabinet();
$(document).ready(function () {
    $('#logout').click(gabinet.logout);
    $('#settings').click(gabinet.settings);
    $('#show-ad-recipes').click(gabinet.addRecipes);
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