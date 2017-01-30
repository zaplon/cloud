function IcdModel() {
    this.inputValue = ko.observable('');
    this.delayedValue = ko.pureComputed(this.inputValue)
        .extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 400 } });

    // Keep a log of the throttled values
    this.loggedValues = ko.observableArray([]);
    this.icd10 = ko.observableArray();
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
        var exclude = [];
        this.icd10().forEach(function(r){
            excludes.push(r.id);
        });
        $.getJSON('/rest/icd/', {limit: 10, search: me.inputValue, exclude: JSON.stringify(exclude)}, function(res){
          me.suggestions(res.results);
        });
    };
}
var icdModel = new IcdModel();
ko.applyBindings(icdModel, $('#icd10')[0]);
icdModel.getSuggestions();