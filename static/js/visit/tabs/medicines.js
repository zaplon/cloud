var medicine = function (data) {
    var record =  {
        id: false, name: '', composition: ko.observable(), dose: ko.observable(), children: ko.observableArray(),
        nfz: ko.observableArray(), selection: ko.observable(), size: ko.observable(), refundation: ko.observable(),
        dosage: ko.observable(), amount: ko.observable()
    };
    record.selection.subscribe(function(newValue){
        $.getJSON('/rest/medicines?limit=10', {parent: newValue.id}, function(res){
            record.children(res.results);
        });
        record.dose(newValue.dose);
        record.composition(newValue.composition);
    });
    record.children.subscribe(function(newValue){
        if (newValue.id)
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
    realisationDate: ko.observable(moment().format('YYYY-MM-DD')),
    //getFormattedDate: function(){ return moment(this.realisationDate(), 'YYYY-MM-DD').format('MM/DD/YYYY') },
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
        JSON.parse(data).forEach(function(d){
           me.medicines().push(medicine(d));
        });
        me.medicines().push(medicine());
    },
    save: function(){
        var data = [];
        var me = this;
        var medicines = this.medicines();
        medicines.forEach(function(medicine, i){
            var m = ko.toJS(medicine);
            if (i < medicines.length-1)
                data.push({id: m.id, amount: m.amount, name: m.name, composition: m.composition, dose: m.dose, size: m.size, dosage: m.dosage,
                refundation: m.refundation, selection: m.selection});
        });
        if (data.length == 0)
            return null;
        return JSON.stringify(data);
    },
    printRecipe: function(){
        $.post('/visit/recipe/', {medicines: this.save(), nfz: this.nfz(), permissions: this.permissions(),
        patient: JSON.stringify(visit.patient()), realisationDate: this.realisationDate(),
            number: $('#use-number').is(':checked') ? 1 : 0}, function(res){
            if (!res.success)
                notie.alert(3, res.message);
            else
                gabinet.showPdf(res.url);
        });
    }
};
if (tabs)
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

