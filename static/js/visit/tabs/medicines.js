var medicinesModel = {
    medicines: ko.observableArray([]),
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
    newMedicine: ko.observable({name: '', composition: '', dose: ''}),
    newChildren: ko.observableArray([]),
    newRefundations: ko.observableArray(),
    newSize: ko.observable(),
    newRefundation: ko.observable(),
    removeMedicine: function(medicine){
        medicinesModel.medicines.remove(medicine);
    },
    addMedicine: function(){
        var newRow = medicinesModel.newMedicine();
        newRow.newChildren = medicinesModel.newChildren();
        medicinesModel.medicines.push(newRow);
        medicinesModel.newChildren([]);
        medicinesModel.newMedicine({name: '', composition: '', dose: ''});
    }
};

$(document).ready(function(){
    ko.applyBindings(medicinesModel, $('#medicines')[0]);
    medicinesModel.newMedicine.subscribe(function(newValue) {
       if (!newValue.id) {
           medicinesModel.newMedicine = {name: '', composition: '', dose: ''};
           return false;
       }
       console.log('selected');
       $.getJSON('/rest/medicines?limit=10', {parent: newValue.id}, function(res){
          medicinesModel.newChildren(res.results);
        });

    });
});

