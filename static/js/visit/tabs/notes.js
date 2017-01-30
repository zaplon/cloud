var notesModel = {
    notes: ko.observableArray(),
    note: ko.observable(),
    addNote: function(){
        var text = this.note();
        $.post('/rest/notes/', {text: text, doctor: gabinet.doctor.id, patient: gabinet.visit.patient.id}, function(res){
            notesModel.notes.push(res);
            notesModel.note('');
        });
    },
    deleteNote: function(note){
        notesModel.notes.remove(note);
    },
    getNotes: function(res){
        $.getJSON('/rest/notes/', {patient: gabinet.visit.patient.id}, function(res){
            notesModel.notes(res);
        });
    }
};
ko.applyBindings(notesModel, $('#notes')[0]);
$(document).ready(function(){
    notesModel.getNotes();
});
