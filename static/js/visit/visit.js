var visit = {
    term: {},
    tabs: [],
    errors: [],
    patient: ko.observable({address: '', pesel: '', name: ''}),
    subMenuName: ko.observable(''),
    subMenu: {
      hidden: ko.observable(true),
      forms: ko.observableArray(),
      showForm: function(form){
        visit.showForm(form.name);
      },
      show: function(){
          this.hidden(!this.hidden());
          if (this.hidden()) {
              $('.page-content').css('padding-top', 166 + 'px');
              $('.control-panel-container').css('padding-top', 136 + 'px');
          }
          else {
              $('.page-content').css('padding-top', 206 + 'px');
              $('.control-panel-container').css('padding-top', 176 + 'px');
          }
      },
      showSkierowania: function(){
          this.subMenu.show();
          this.subMenu.forms([
              {title: 'Skierowanie do szpitala', name: 'hospital.pdf'},
              {title: 'Skierowanie do szpitala', name: 'hospital.pdf'}
          ]);
          if (this.subMenuName().length == 0)
            this.subMenuName('skierowania');
          else
            this.subMenuName('')
      }
    },
    saveVisit: function () {
        var me = this;
        tabs.forEach(function (tab) {
            if (typeof(tab.model.save) == 'undefined')
                data = null;
            else
                data = tab.model.save();
            me.tabs.push({data: data, title: tab.title, id:tab.id});
        });
        if (me.errors.length == 0) {
            $.post(window.location.pathname, {data: JSON.stringify(me.tabs)}, function(res){
              if (res.success){
                window.location.pathname = '/';
              }
              else {
                    for (e in res.errors){
                        var tab = tabs.filter(function(r){ return r.title == e });
                        if (tab.length > 0){
                            $('a[href="#'+tab[0].title+'"').addClass('tab-error');
                            tab[0].model.errors(res.errors[e]);
                        }
                    };
              }
            });
        }
    },
    cancelVisit: function () {
        $.post(window.location.pathname, {'cancel': true}).success(function (res) {
            window.location.pathname = '/';
        });
    },
    templates: ko.observableArray(),
    loadTemplates: function () {
        $.getJSON("/rest/templates/", function (data) {
            visit.templates(data);
        });
    },
    currentTab: $('.visit-tab:visible').attr('id'),
    putTemplate: function () {

    },
    showForm: function(form){
        params = {};
        params.pesel = this.patient().pesel;
        gabinet.showForm(form, params);
    },
    printVisit: function(){
        $.get('/visit/pdf/'+visit.term.id + '/?as_link=1', function(res){
          gabinet.showPdf(res, 'Historia choroby', false);
        });
    }
};

ko.applyBindings(visit, $('.control-panel-container')[0]);
ko.applyBindings(visit, $('#visit-menu')[0]);
ko.applyBindings(visit.subMenu, $('#visit-sub-menu')[0]);
ko.applyBindings(visit, $('#patient')[0]);

$(document).ready(function () {
    $('.tab-link').click(function () {
        visit.currentTab = $(this).attr('href');
        visit.currentTab = visit.currentTab.substr(1, visit.currentTab.length - 1);
        console.log(visit.currentTab);
        visit.loadTemplates();
    });
    visit.loadTemplates();
});