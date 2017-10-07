formViewModel = {
    name: '',
    niceName: '',
    validate: function () {
        var requiredFields = $('input,textarea,select').filter('[required]:visible');
        var test = true;
        var extraTest = true;
        requiredFields.each(function (f) {
            if (!$(f).val()) {
                test = false;
                $(f).addClass('field-error');
            }
            else
                $(f).removeClass('field-error');
        });
        if (formViewModel.extraValidation)
            extraTest = formViewModel.extraValidation();
        return test && extraTest;
    },
    getData: function () {
        var html = $($('#form-editor iframe').contents()[0])[0].childNodes[0].cloneNode(true);
        var htmlJq = $(html);
        var inputs = htmlJq.find('input');
        var textareas = htmlJq.find('textarea');
        var selects = htmlJq.find('select');
        inputs.each(function (index, i) {
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
            s.outerHTML = '<span>' + $(s).val() +'</span>';
        });
        return html.outerHTML;
    },
    makePdf: function () {
        var data = formViewModel.getData();
        $.post('/forms/edit_form/', {data: data}, function (res) {
            var params = {tmp: res.tmp, print: true, template_name: $('#form-editor iframe').attr('data-template')};

            params['as_file'] = 1;
            $.get('/forms/show_form/?' + $.param(params)).success(function(res){
                rp.print(res);
            });

            //window.location.href = '/forms/show_form/?' + $.param(params);
        });
    },
    sendToElo: function () {
        if (!this.validate())
            return;
        var data = formViewModel.getData();
         $.post('/forms/edit_form/', {data: data}, function (res) {
            $.get('/forms/show_form/', {elo: true, print: true, tmp: res.tmp, nice_name: formViewModel.niceName}, function (res) {
                alert('dokument przesłano do archiwum');
            }).fail(function () {
                alert('wystąpił błąd!')
            });
        });
    },
    saveTemporary: function () {
        $.post('/forms/edit_form/', {
            data: formViewModel.getData(),
            tmp: true,
            name: formViewModel.name,
            nice_name: formViewModel.niceName
        }, function (res) {
            alert('zapisano wersję roboczą');
        });
    },
    close: function () {
        $('button.close').click();
    }
};