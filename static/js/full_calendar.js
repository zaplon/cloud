fullCalendarModel = {
    doctors: ko.observableArray([]),
    loadDoctors: function(params){
        if (params === undefined)
            params = {};
        var me = this;
        $.get('/rest/doctors/', params, function(res){
            me.doctors(res);
        });
    }
};

$(document).ready(function(){
    ko.applyBindings(fullCalendarModel, $('#doctors-list')[0]);
    ko.applyBindings(fullCalendarModel, $('#calendar-filters')[0]);
    fullCalendarModel.loadDoctors();
});