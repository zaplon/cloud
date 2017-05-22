function ServicesModel() {
    this.inputValue = ko.observable('');
    this.data = [];
    this.delayedValue = ko.pureComputed(this.inputValue)
        .extend({rateLimit: {method: "notifyWhenChangesStop", timeout: 400}});
    this.services = ko.observableArray([]);
    this.suggestions = ko.observableArray();
    this.delayedValue.subscribe(function (val) {
        this.getSuggestions();
    }, this);
    this.addService = function (service) {
        servicesModel.services.push(service);
        servicesModel.suggestions.remove(service);
    };
    this.removeService = function (service) {
        servicesModel.services.remove(service);
    };
    this.getSuggestions = function () {
        var me = this;
        if (this.data.length == 0) {
            $.get('http://www.rentgen.pl/services-list.php').done(function (res) {
                console.log(res);
            }).fail(function (res) {
                var text = res.responseText;
                try {
                    text = JSON.parse(text.replace("\\",''));
                }
                catch(error) {
                    text = [];
                    return;
                }
                var id = 1;
                for (var group in text) {
                    text[group].forEach(function (item) {
                        me.data.push({name: item, group: group, id: id});
                        id++;
                    });
                }
                me.getSuggestions();
            });
            return;
        }
        var excludes = [];
        this.services().forEach(function (r) {
            excludes.push(r.id);
        });
        var counter = 0;
        var res = this.data.filter(function (d) {
            var val = me.inputValue().toLowerCase();
            if (excludes.indexOf(d.id) == -1 && counter < 10 && (!val ||
                (d.name.toLowerCase().indexOf(val) > -1 || d.group.toLowerCase().indexOf(val)) > -1)) {
                counter += 1;
                return true;
            }
        });
        me.suggestions(res);
    };
    this.parse = function (data) {
        if (data)
            this.services(data);
    };
    this.save = function () {
        return this.services();
    };
    this.print = function () {
        var add_icd = $('#print-services-icd').is(':checked');
        if (add_icd)
            var icd = tabs.filter(function(t){return (t.title == 'Rozpoznanie')})[0].model.icd10();
        else
            var icd = undefined;
        $.get('/visit/pdf/services/', {'services': JSON.stringify(this.services()), icd: icd,
            'patient': JSON.stringify(visit.patient()), 'as_link': 1}, function(res){
            gabinet.showPdf(res, 'Skierowanie');
        });
    };
    this.errors = ko.observable();
}
var servicesModel = new ServicesModel();
ko.applyBindings(servicesModel, $('#services')[0]);
servicesModel.getSuggestions();

tabs[tabs.length - 1].model = servicesModel;
