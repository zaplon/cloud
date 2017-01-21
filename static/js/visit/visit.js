var viewModel = {
    saveVisit: function () {
    },
    cancelVisit: function () {
        $.post(window.location.pathname, {'cancel': true}).success(function (res) {
            window.location.pathname = '/';
        });
    },
    templates: ko.observableArray(),
    loadTemplates: function () {
        $.getJSON("/rest/templates/", function (data) {
            viewModel.templates(data);
        });
    },
    currentTab: $('.visit-tab:visible').attr('id')
};

ko.applyBindings(viewModel);

$(document).ready(function () {
    $('.tab-link').click(function () {
        viewModel.currentTab = $(this).attr('href');
        viewModel.currentTab = viewModel.currentTab.substr(1, viewModel.currentTab.length-1);
        console.log(viewModel.currentTab);
        viewModel.loadTemplates();
    });
    viewModel.loadTemplates();
});