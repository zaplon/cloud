var medicine = function (data) {
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
    for (d in data){
        if (d in record)
            if (typeof(record[d]) == 'function')
                record[d](data[d]);
            else
                record[d] = data[d];
    }
    return record;
};
var medicinesModel = {
    medicines: ko.observableArray([medicine()]),
    realisationDate: ko.observable(),
    nfz: ko.observable(7),
    permissions: ko.observable('X'),
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
    parse: function(data){
        var me = this;
        me.medicines([]);
        data.forEach(function(d){
           me.medicines().push(medicine(d));
        });
        me.medicines().push(medicine());
    },
    save: function(){
        var data = [];
        var me = this;
        var medicines = this.medicines();
        medicines.forEach(function(m, i){
            if (i < medicines.length-1)
                data.push({id: m.id, name: m.name, composition: m.composition(), dose: m.dose(), size: m.size(),
                refundation: m.refundation(), selection: m.selection()});
        });
        return data;
    },
    printRecipe: function(){
        $.post('/visit/recipe/', {medicines: this.save(), nfz: this.nfz(), permissions: this.permissions(),
        patient: visit.patient}, function(res){
            gabinet.showPdf(res.url);
        });
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

