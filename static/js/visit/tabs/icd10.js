function IcdModel() {
    this.inputValue = ko.observable('');
    this.delayedValue = ko.pureComputed(this.inputValue)
        .extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 400 } });
    this.icd10 = ko.observableArray([]);
    this.suggestions = ko.observableArray();
    this.delayedValue.subscribe(function (val) {
        this.getSuggestions();
    }, this);
    this.addIcd = function (icd) {
        icdModel.icd10.push(icd);
        icdModel.suggestions.remove(icd);
    };
    this.removeIcd = function (icd) {
        icdModel.icd10.remove(icd);
    };
    this.getSuggestions = function(){
        var me = this;
        var excludes = [];
        this.icd10().forEach(function(r){
            excludes.push(r.id);
        });
        $.getJSON('/rest/icd/', {limit: 10, search: me.inputValue, exclude: JSON.stringify(excludes)}, function(res){
          me.suggestions(res.results);
        });
    };
    this.parse = function(data){
        if (data)
            this.icd10(data);
    };
    this.save = function(){
        return this.icd10();
    };
    this.errors = ko.observable();
}
var icdModel = new IcdModel();
ko.applyBindings(icdModel, $('#icd10')[0]);
icdModel.getSuggestions();

tabs[tabs.length-1].model = icdModel;