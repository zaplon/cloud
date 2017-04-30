var visit = {
    archive: {
        documents: ko.observableArray(),
        getDocument: function (d) {
            $.get('/rest/results/' + d.id, {}, function (res) {

            });
        },
        getArchive: function () {
            $.get('/rest/results/', {pesel: visit.patient().pesel}, function (res) {
                var me = this;
                res.forEach(function (r) {
                    me.documents.push(r);
                });
            })
        },
        addDocument: function () {
            $.get('/get-form', {module: 'result.forms', class: 'ResultForm'}, function (res) {
                var save = "<button id='addArchiveDocument' class='btn btn-primary'>Dodaj</button>";
                gabinet.showModal('Dodaj plik', res.form_html, save);
                $('#addArchiveDocument').click(function () {
                    var form = $(this).parent().parent().find('form');
                    $.ajax({
                        // Your server script to process the upload
                        url: '/get-form/',
                        type: 'POST',
                        // Form data
                        data: new FormData(form[0]),
                        // Tell jQuery not to process data or worry about content-type
                        // You *must* include these options!
                        cache: false,
                        contentType: false,
                        processData: false,
                        success: function (res) {
                            if (res.success) {
                                $('button.close').click();
                            }
                            else {
                                form.parent().html(res.form_html);
                            }
                        },
                        // Custom XMLHttpRequest
                        xhr: function () {
                            var myXhr = $.ajaxSettings.xhr();
                            if (myXhr.upload) {
                                // For handling the progress of the upload
                                myXhr.upload.addEventListener('progress', function (e) {
                                    if (e.lengthComputable) {
                                        $('progress').attr({
                                            value: e.loaded,
                                            max: e.total,
                                        });
                                    }
                                }, false);
                            }
                            return myXhr;
                        },
                    });
                });
            });
        }
    },
    term: {},
    tabs: [],
    errors: [],
    patient: ko.observable({address: '', pesel: '', name: ''}),
    subMenuName: ko.observable(''),
    subMenu: {
        hidden: ko.observable(true),
        forms: ko.observableArray(),
        showForm: function (form) {
            if (form)
                visit.showForm(form.name);
        },
        show: function (hide) {
            if (this == window)
                return;
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
        showSkierowania: function () {
            if (this == window)
                return;
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
        showMedycynaPracy: function () {
            if (this == window)
                return;
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
        showOrzeczenia: function () {
            if (this == window)
                return;
        }
    },
    saveVisit: function (tmp) {
        if (this == window)
            return;
        var me = this;
        tabs.forEach(function (tab) {
            if (typeof(tab.model.save) == 'undefined')
                data = null;
            else
                data = tab.model.save();
            me.tabs.push({data: data, title: tab.title, id: tab.id});
        });
        if (me.errors.length == 0) {
            $.ajax({
                type: "POST",
                url: window.location.pathname,
                data: {
                    data: JSON.stringify(visit.tabs),
                    tmp: tmp ? true : false
                },
                success: function (res) {
                    if (res.success) {
                        if (!tmp)
                            window.location.pathname = '/';
                    }
                    else {
                        for (e in res.errors) {
                            var tab = tabs.filter(function (r) {
                                return r.title == e
                            });
                            if (tab.length > 0) {
                                $('a[href="#' + tab[0].title + '"').addClass('tab-error');
                                tab[0].model.errors(res.errors[e]);
                            }
                        }
                    }
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
    putTemplate: function (template) {
        var tab = tabs.filter(function (tab) {
            return tab.title == template.tab_title;
        });
        if (tab.length == 0)
            return;
        tab = tab[0];
        tab.model.parse(template.text);
        return true;
    },
    addTemplate: function () {
        $.get('/get-form/', {module: 'visit.forms', class: 'TemplateForm'}, function (res) {
            var save = "<button id='AddTemplate' class='btn btn-primary'>Dodaj</button>";
            gabinet.showModal('Dodaj szablon', res.form_html, save);
            $('#AddTemplate').click(function(){
                var form = $(this).parent().parent().find('form');
                var data = form.serialize();
                $.post('/get-form/', {module: 'visit.forms', class: 'TemplateForm', data: data}, function (res) {
                    if (res.success){
                        $('button.close').click();
                    }
                    else {
                        form.parent().html(res.form_html);
                    }
                });
            });
        });
    },
    removeTemplate: function(){

    },
    showForm: function (form) {
        params = {};
        params.pesel = this.patient().pesel;
        gabinet.showForm(form, params);
    },
    printVisit: function () {
        $.get('/visit/pdf/' + visit.term.id + '/?as_link=1', function (res) {
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
