var today = new Date();
var todayStr = today.getFullYear() + '-' + (today.getMonth() < 9 ? ('0' + (today.getMonth() + 1)) : (today.getMonth() + 1))
    + '-' + (today.getDate() < 10 ? ('0' + today.getDate()) : today.getDate());
var todayJoin = todayStr.split('-').reverse();

putPostal = function(code){
    for (var i=0;i<=5;i++){
        $('.postal' + i).val(code[i]);
    }
};

putSplittedDate = function(e, inputPrefix){
            if (e.date < new Date()) {
                e.preventDefault(); // Prevent to pick the date
            }
            else {
                var day = "" + e.date.getDate();
                var month = "" + (e.date.getMonth() < 10 ? '0' + (e.date.getMonth() + 1) : e.date.getMonth());
                var year = "" + e.date.getFullYear();
                $('input[name="' + inputPrefix + 1 +'"]').val(day[0]);
                $('input[name="' + inputPrefix + 2 +'"]').val(day[1]);
                $('input[name="' + inputPrefix + 3 +'"]').val(month[1]);
                $('input[name="' + inputPrefix + 4 +'"]').val(month[2]);
                $('input[name="' + inputPrefix + 5 +'"]').val(year.substr(0, 2));
                $('input[name="' + inputPrefix + 6 +'"]').val(year.substr(2, 4));
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

function crossOther(el, event){
  if ($(el).attr('data-target')){
      $('#'+$(el).attr('data-target')).addClass('cross-out');
      $(el).removeClass('cross-out');
      return;
  }
  $(el).parent().parent().find('.crossable').each(function(i, el){
      $(el).addClass('cross-out');
  });
  $(el).removeClass('cross-out');
};

$(document).ready(function () {
    try {
     $('[data-toggle="datepicker"]').datepicker({language: 'pl-PL', format: 'yyyy-MM-dd'});
    }
    catch(err){
    }

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
        crossOther(this, event);
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

