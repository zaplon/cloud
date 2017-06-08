fullCalendarModel = {
    doctors: ko.observableArray([]),
    dateFrom: ko.observable(),
    selectedSpecialization: ko.observable(),
    selectedLocalization: ko.observable(),
    specializations: ko.observableArray(),
    localizations: ko.observableArray(),
    loadDoctors: function(params){
        if (params === undefined)
            params = {};
        if (this.selectedSpecialization())
            params.specialization = this.selectedSpecialization().id
        if (this.selectedLocalization())
            params.localization = this.selectedLocalization().id
        var me = this;
        $.get('/rest/doctors/', params, function(res){
            me.doctors(res);
        });
    },
    loadDoctorCalendar: function(doctor){
        $('#calendar').fullCalendar('refetchEvents');
    }
};

$(document).ready(function(){
    ko.applyBindings(fullCalendarModel, $('#doctors-list')[0]);
    ko.applyBindings(fullCalendarModel, $('#calendar-filters')[0]);
    fullCalendarModel.loadDoctors();
});
