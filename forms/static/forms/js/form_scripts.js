var today = new Date();
var todayStr = today.getFullYear() + '-' + (today.getMonth() < 9 ? ('0' + (today.getMonth() + 1)) : (today.getMonth() + 1))
    + '-' + (today.getDate() < 10 ? ('0' + today.getDate()) : today.getDate());

function crossOut(el, event) {
    if (event.target.type && (event.target.type.indexOf('select') > -1 || event.target.type == 'text'))
        return;
    if ($(el).hasClass('cross-out'))
        $(el).removeClass('cross-out');
    else
        $(el).addClass('cross-out');
};

$(document).ready(function () {
    if (parent.visit.formParams)
        for (param in parent.visit.formParams) {
            if ($('input[name="' + param + '"]').length > 0)
                $('input[name="' + param + '"]').val(parent.visit.formParams[param]);
            if ($('textarea[name="' + param + '"]').length > 0)
                $('textarea[name="' + param + '"]').html(parent.visit.formParams[param]);
        }
    ;
    //orzeczeni zdolnosc do pracy
    $('.cross li').addClass('crossable');

    $('.crossable').click(function (event) {
        crossOut(this, event);
    });

    $('input[name="today-date"]').each(function(i, el){
        $(el).val(todayStr);
    });
    $('input[name="city&date"]').each(function(i, el){
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

