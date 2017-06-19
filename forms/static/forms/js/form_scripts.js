var today = new Date();
var todayStr = today.getFullYear() + '-' + (today.getMonth() < 10 ? ('0' + today.getMonth()) : today.getMonth())
+ '-' + (today.getDate() < 10 ? ('0' + today.getDate()) : today.getDate());

function crossOut(el){
    if (event.target.type && (event.target.type.indexOf('select') > -1 || event.target.type == 'text'))
        return;
    if ($(el).hasClass('cross-out'))
        $(el).removeClass('cross-out');
    else
        $(el).addClass('cross-out');
};

$(document).ready(function(){
    if (parent.visit.formParams)
        for (param in parent.visit.formParams){
            if ($('input[name="'+param+'"]').length > 0)
                $('input[name="'+param+'"]').val(parent.visit.formParams[param]);
            if ($('textarea[name="'+param+'"]').length > 0)
                $('textarea[name="'+param+'"]').html(parent.visit.formParams[param]);
        };
    //orzeczeni zdolnosc do pracy
    $('.cross li').addClass('crossable');

    $('.crossable').click(function(event){
       crossOut(this, event);
    });

});

