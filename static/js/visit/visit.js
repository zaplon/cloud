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
      show: function(hide){
          this.hidden(hide);
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
          this.subMenu.forms([
              {title: 'Skierowanie do szpitala', name: 'hospital.pdf'},
              {title: 'Skierowanie do poradni specjalistycznej', name: 'poradnia_specjalistyczna.pdf'}
          ]);
          if (this.subMenuName() == 'skierowania') {
              this.subMenu.show(1);
              this.subMenuName('');
          }
          else {
              this.subMenuName('skierowania');
              this.subMenu.show();
          }
      },
      showMedycynaPracy: function(){
          this.subMenu.forms([
              {title: 'Karta badania profilaktycznego', name: 'profilactic.pdf'},
              {title: 'Karta badania lekarskiego', name: 'doctor.pdf'},
              {title: 'Karta badania Prawo Jazdy', name: 'driver.pdf'}
          ]);
        if (this.subMenuName() == 'medycyna_pracy') {
            this.subMenuName('');
            this.subMenu.show(1);
        }
          else {
            this.subMenuName('medycyna_pracy');
            this.subMenu.show();
        }
      },
      showOrzeczenia: function(){

      }
    },
    saveVisit: function (tmp) {
        var me = this;
        tabs.forEach(function (tab) {
            if (typeof(tab.model.save) == 'undefined')
                data = null;
            else
                data = tab.model.save();
            me.tabs.push({data: data, title: tab.title, id:tab.id});
        });
        if (me.errors.length == 0) {
            $.post(window.location.pathname, {data: JSON.stringify(me.tabs), tmp: true ? tmp : false}, function(res){
              if (res.success){
                if (!tmp)
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
    putTemplate: function (template){
        var tab = tabs.filter(function(tab){ return tab.title == template.tab_title; });
        if (tab.length == 0)
            return;
        tab = tab[0];
        tab.model.parse(template.text);
        return true;
    },
    addTemplate: function(){
        $.get('get-form', {module: 'visit.forms', class: 'TermplateForm', tab: 1}, function(res){
            var save = "<button class='btn btn-default'>Anuluj</button><button class='btn btn-success'></button>";
            gabinet.showModal('Dodaj szablon', res.form_html, save);
        });
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
