var today = new Date();
var todayStr = today.getFullYear() + '-' + (today.getMonth() < 10 ? ('0' + today.getMonth()) : today.getMonth())
+ '-' + (today.getDate() < 10 ? ('0' + today.getDate()) : today.getDate());

function crossOut(el){
    if ($(el).hasClass('cross-out'))
        $(el).removeClass('cross-out');
    else
        $(el).addClass('cross-out');
};

$(document).ready(function(){
    if (parent.SPSR)
        for (param in parent.SPSR.params){
            if ($('input[name="'+param+'"]').length > 0)
                $('input[name="'+param+'"]').val(parent.SPSR.params[param]);
            if ($('textarea[name="'+param+'"]').length > 0)
                $('textarea[name="'+param+'"]').html(parent.SPSR.params[param]);
        };
    //orzeczeni zdolnosc do pracy
    $('.cross li').addClass('crossable');

    $('.crossable').click(function(){
       crossOut(this);
    });

});

