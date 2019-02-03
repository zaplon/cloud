var today = new Date();
var todayStr = today.getFullYear() + '-' + (today.getMonth() < 9 ? ('0' + (today.getMonth() + 1)) : (today.getMonth() + 1))
    + '-' + (today.getDate() < 10 ? ('0' + today.getDate()) : today.getDate());
var todayJoin = todayStr.split('-').reverse();

putPostal = function (code) {
    var code = code.replace('-', '');
    for (var i = 0; i <= 5; i++) {
        $('input[name=postal' + (i + 1) + ']').val(code[(i + 1)]);
    }
};

putSplittedDate = function (e, inputPrefix) {
    if (e.date < new Date()) {
        e.preventDefault(); // Prevent to pick the date
    }
    else {
        var day = "" + e.date.getDate();
        var month = "" + (e.date.getMonth() < 10 ? '0' + (e.date.getMonth() + 1) : e.date.getMonth());
        var year = "" + e.date.getFullYear();
        $('input[name="' + inputPrefix + 1 + '"]').val(day[0]);
        $('input[name="' + inputPrefix + 2 + '"]').val(day[1]);
        $('input[name="' + inputPrefix + 3 + '"]').val(month[0]);
        $('input[name="' + inputPrefix + 4 + '"]').val(month[1]);
        $('input[name="' + inputPrefix + 5 + '"]').val(year.substr(0, 2));
        $('input[name="' + inputPrefix + 6 + '"]').val(year.substr(2, 4));
    }
};

function crossOut(el, event) {
    if (event.target.type && (event.target.type.indexOf('select') > -1 || event.target.type == 'text'))
        return;
    if ($(el).hasClass('cross-out'))
        $(el).removeClass('cross-out');
    else
        $(el).addClass('cross-out');
};

function crossOther(el, event) {
    if ($(el).attr('data-target')) {
        $('#' + $(el).attr('data-target')).addClass('cross-out');
        $(el).removeClass('cross-out');
        return;
    }
    $(el).parent().parent().find('.crossable').each(function (i, el) {
        $(el).addClass('cross-out');
    });
    $(el).removeClass('cross-out');
};

$(document).ready(function () {
    try {
        $('[data-toggle="datepicker"]').datepicker({language: 'pl-PL', format: 'yyyy-MM-dd'});
    }
    catch (err) {
    }
    console.log(window.location);
    var params = {};
    var paramsStr = window.location.href.split('?')[1];
    if (paramsStr)
        paramsStr.split('&').forEach(function(val){
           var parts = val.split('=');
           params[parts[0]] = decodeURIComponent(parts[1]);
        });
    console.log(params);
    window.params = params;
    for (param in params) {
        if ($('input[name="' + param + '"]').length > 0)
            $('input[name="' + param + '"]').val(params[param]);
        if ($('textarea[name="' + param + '"]').length > 0)
            $('textarea[name="' + param + '"]').html(params[param]);
    }
    if (params.header_left) {
        $('#document-header-left').html(params.header_left);
    }
    if (params.header_right) {
        $('#document-header-right').html(params.header_right);
    }
    //orzeczeni zdolnosc do pracy
    $('.cross li').addClass('crossable');

    $('.crossable').click(function (event) {
        crossOther(this, event);
    });

    $('input[name="today-date"]').each(function (i, el) {
        $(el).val(todayStr);
    });
    $('input[name="city&date"]').each(function (i, el) {
        $(el).val('Warszawa, ' + todayStr);
    });

    $('.group').click(function () {
        var t = $(this);
        if (t.hasClass('selected')) {
            t.removeClass('selected');
            t.find('.mark').html('&nbsp;');
        }
        else {
            t.addClass('selected');
            t.find('.mark').html('X');
        }
        $('.group:not(.selected)').addClass('cross-out');
        $('.group.selected').removeClass('cross-out');
    });

});

function getData() {
    var html = this.document.documentElement.cloneNode(true);
    var htmlJq = $(html);
    var inputs = htmlJq.find('input');
    var textareas = htmlJq.find('textarea');
    var selects = htmlJq.find('select');
    inputs.each(function (index, i) {
        if ($(i).attr('type') == 'radio')
            if ($(i).is(':checked'))
                $(i).attr('checked', '1');
            else
                $(i).removeAttr('checked');
        if ($(i).attr('type') == 'checkbox')
            if (i.checked)
                $(i).attr('checked', '1');
            else
                $(i).removeAttr('checked');
        else
            $(i).attr('value', $(i).val());
    });
    textareas.each(function (index, t) {
        $(t).html(t.value);
    });
    selects.each(function (index, s) {
        s.outerHTML = '<span>' + $(s).val() + '</span>';
    });
    return html.outerHTML.replace('" type="date', '');
}

function makePdf(event) {
    $.post('/backend/forms/edit_form/', {data: getData()}, function (res) {
        var params = {tmp: res.tmp, print: true, template_name: event.data.name, pages: event.data.pages};
        params['as_file'] = 1;
        if ('save' in event.data){
            params['save'] = 1;
            params['user_id'] = event.data.user_id;
            params['patient_id'] = event.data.patient_id;
            params['nice_name'] = event.data.nice_name;
        }
        $.get('/backend/forms/show_form/?' + $.param(params), function (res) {
            if ('save' in event.data)
                event.source.postMessage('save', event.origin);
            else
                event.source.postMessage(res, event.origin);
        });

    });
}


function receiveMessage(event) {
    // Do we trust the sender of this message?
    //if (event.origin !== "http://example.com:8080")
    //  return;
    makePdf(event)
}

window.addEventListener("message", receiveMessage, false);
