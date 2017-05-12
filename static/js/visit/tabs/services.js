function ServicesModel() {
    this.inputValue = ko.observable('');
    this.data = [];
    this.delayedValue = ko.pureComputed(this.inputValue)
        .extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 400 } });
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
    this.getSuggestions = function(){
        var me = this;
        if (this.data.length == 0){
          $.getJSON('', function(res){
            res.forEach(function(r){
              me.data.push({name: '', group: ''});
            });
            me.getSuggestions();
          });
          return;
        }
        var excludes = [];
        this.services().forEach(function(r){
            excludes.push(r.id);
        });
        var counter = 0;
        var res = this.data.filter(function(d){ 
          if (excludes.indexOf(d.id) == -1 && counter < 10 && (!me.inputValue || (d.name.indexOf(me.inputValue) > -1 || d.group.indexOf(me.inputValue)) > -1) ){
            counter += 1;
            return true;
          }  
        });
        me.suggestions(res);
    };
    this.parse = function(data){
        if (data)
            this.services(data);
    };
    this.save = function(){
        return this.services();
    };
    this.errors = ko.observable();
}
var servicesModel = new ServiceModel();
ko.applyBindings(servicesModel, $('#services')[0]);
servicesModel.getSuggestions();

tabs[tabs.length-1].model = servicesModel;
