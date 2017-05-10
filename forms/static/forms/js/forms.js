formViewModel = {
    name: '',
    validate: function(){
        var requiredFields = $('input,textarea,select').filter('[required]:visible');
        var test = true;
        var extraTest = true;
        requiredFields.each(function(f){
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
    getData: function(){
      return $('#form-editor iframe')[0].contentDocument.getElementsByTagName('html')[0].outerHTML;
    },
    makePdf: function(){
        var data = formViewModel.getData();
        $.post('/forms/edit_form/', {data: data}, function(res){
            var params = {tmp: res.tmp, print: true, template_name: $('#form-editor iframe').attr('data-template')};
            window.location.href = '/forms/show_form/?' + $.param(params);
        });
    },
    sendToElo: function(){
        var data = formViewModel.getData();
    },
    saveTemporary: function(){
        $.post('/forms/edit_form/', {data: formViewModel.getData(), tmp: true, name: formViewModel.name}, function(res){
            alert('zapisano wersję roboczą');
        });
    },
    close: function(){
        $('#form-editor-container').remove();
    }
};