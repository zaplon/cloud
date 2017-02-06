/// <reference path="types/jquery.d.ts" />
/// <reference path="types/bootstrap.d.ts" />

class Gabinet {
    doctor: {};
    pageLimit: number;
    constructor(){
        this.pageLimit = 10;
    };
    logout() {
        $.post('/account/logout/', function(){
            window.location.href = '/';
        });
    };
    transformTableResponse(res){
        return {total: res.count, rows: res.results}
    };
    settings(){
        $.get('/profile/settings/', function(res){
            $('#hidden').append(res);
            $.getScript('/static/js/user_profile/settings.js', function(){ ready(); });
            $('#settings-modal').modal({show: true, keyboard: true});
        });
    };
    showPdf(url, title, binary=false){
        var width = $(document).width();
        if (width < 900)
            width = width - 30;
        else
            width = 870;
        var height = $(document).height()*0.75;
        var save = '<button type="button" class="btn btn-primary">Save changes</button>';
        if (!binary)
            var pdf = `<object data="${url}" type="application/pdf" width="${width}" height="${height}">`;
        else
            var pdf = `<embed data="data:application/pdf;base64,${url}" type="application/pdf" width="${width}" height="${height}">
            </embed>`;
        if (!title)
            title = 'Dokument';
        this.showModal(title, pdf, save, 'modal-lg');
    };
    showModal(title, body, save, size=''){
        var modal = `<div id='pdf-modal' class="modal fade">
          <div class="modal-dialog ${size}" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">${title}</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body">
                ${body}
              </div>
              <div class="modal-footer">
                ${save}
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Zamknij</button>
              </div>
            </div>
          </div>
        </div>`;
        $('#hidden').html(modal);
        $('#pdf-modal').modal({show: true, keyboard: true});
    };
    showForm(form, params){
        if (typeof(params) != "undefined"){
            var params_str = '?';
            for (p in params)
                params_str += p + '=' + params[p] + '&';
            params_str = params_str.substr(0, params_str.length-2);
        }
        if (typeof(params) == "undefined")
            var url = `/static/forms/${form}`;
        else
            var url = `/static/forms/${form}/${params_str}`;
        this.showPdf(url);
    };
}

var gabinet = new Gabinet();

$(document).ready(function(){
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
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});