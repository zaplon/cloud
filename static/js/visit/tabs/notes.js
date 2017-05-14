var notesModel = {
    notes: ko.observableArray(),
    note: ko.observable(),
    dontSave: true,
    addNote: function(){
        var text = this.note();
        $.post('/rest/notes/', {text: text, doctor: gabinet.doctor.id, patient: visit.patient().id}, function(res){
            notesModel.notes.push(res);
            notesModel.note('');
        });
    },
    deleteNote: function(note){
        $.ajax({
            method: 'DELETE',
            url: '/rest/notes/' + note.id,
            success: function(res){
                notesModel.notes.remove(note);
            },
            error: function(res){

            }
        });

    },
    getNotes: function(res){
        $.getJSON('/rest/notes/', {patient: visit.patient.id}, function(res){
            notesModel.notes(res);
        });
    },
    parse: function(){

    }
};
ko.applyBindings(notesModel, $('#notes')[0]);
tabs[tabs.length-1].model = notesModel;
$(document).ready(function(){
    notesModel.getNotes();
});
