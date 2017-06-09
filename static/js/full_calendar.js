fullCalendarModel = {
    doctors: ko.observableArray([]),
    dateFrom: ko.observable(moment(new Date()).format('DD-MM-YYYY')),
    selectedSpecialization: ko.observable(),
    selectedService: ko.observable(),
    selectedLocalization: ko.observable(),
    specializations: ko.observableArray(),
    localizations: ko.observableArray(),
    services: ko.observableArray(),
    doctor: {},
    doctorFilter: ko.observable('');
    loadDoctors: function(params){
        if (params === undefined)
            params = {};
        if (this.selectedSpecialization())
            params.specialization = this.selectedSpecialization().id;
        if (this.selectedLocalization())
            params.localization = this.selectedLocalization().id;
        var me = this;
        params.calendar = 1;
        $.get('/rest/doctors/', params, function(res){
            me.doctors(res);
        });
    },
    loadDoctorCalendar: function(doctor){
        fullCalendarModel.doctor = doctor;
        $('#calendar').fullCalendar('refetchEvents');
    }
};

$(document).ready(function(){
    ko.applyBindings(fullCalendarModel, $('#doctors-list')[0]);
    ko.applyBindings(fullCalendarModel, $('#calendar-filters')[0]);
    $('#date-from').datepicker({
        format: 'dd-mm-yyyy',
        autoclose: true,
        startDate: '+1d',
        minDate: 0

    });
    fullCalendarModel.loadDoctors();
});
