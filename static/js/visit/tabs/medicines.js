var medicine = function () {
    var record =  {
        id: false, name: '', composition: ko.observable(), dose: ko.observable(), children: ko.observableArray(),
        nfz: ko.observableArray(), selection: ko.observable(), size: ko.observable(), refundation: ko.observable()
    };
    record.selection.subscribe(function(newValue){
        $.getJSON('/rest/medicines?limit=10', {parent: newValue.id}, function(res){
            record.children(res.results);
        });
        record.dose(newValue.dose);
        record.composition(newValue.composition);
    });
    record.children.subscribe(function(newValue){
        $.getJSON('/rest/refundations?limit=10', {parent: newValue.id}, function(res){
            record.nfz(res.results);
        });
    });
    return record;
};
var medicinesModel = {
    medicines: ko.observableArray([medicine()]),
    getMedicines: function (searchTerm, callback) {
        $.ajax({
            dataType: "json",
            url: "/rest/medicine_parents/?limit=10",
            data: {
                query: searchTerm
            }
        }).done(function(res){
            res = res.results;
            callback(res);
        });
    },
    removeMedicine: function (medicine) {
        medicinesModel.medicines.remove(medicine);
    },
    addMedicine: function () {
        var newRow = medicine();
        medicinesModel.medicines.push(newRow);
    },
    parse: function(){

    }
};

tabs[tabs.length-1].model = medicinesModel;

$(document).ready(function () {
    ko.applyBindings(medicinesModel, $('#medicines')[0]);
    //medicinesModel.selection.subscribe(function(newValue) {
    //   if (!newValue.id) {
    //       medicinesModel.newMedicine = {name: '', composition: '', dose: ''};
    //       return false;
    //   }
    //   console.log('selected');
    //   $.getJSON('/rest/medicines?limit=10', {parent: newValue.id}, function(res){
    //      medicinesModel.newChildren(res.results);
    //    });
    //
    //});
});

