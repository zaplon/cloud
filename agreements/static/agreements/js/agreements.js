$(document).ready(function () {
    $('.agreement-body').bind('scroll', chk_scroll);
    chk_scroll({currentTarget: $('.agreement-body')});
});

function chk_scroll(e) {
    var elem = $(e.currentTarget);
    if (elem[0].scrollHeight - elem.scrollTop() == elem.outerHeight()) {
        $('#agreement-confirm').removeAttr('disabled');
    }
}