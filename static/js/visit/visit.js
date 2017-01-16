var viewModel = {
    saveVisit: function(){},
    cancelVisit: function(){
        $.post(window.location.pathname, {'cancel': true}).success(function(res){
           window.location.pathname = '/';
        });
    }
};

ko.applyBindings(viewModel);