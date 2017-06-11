fullCalendarModel = {
    doctors: ko.observableArray([]),
    dateFrom: ko.observable(moment(new Date()).format('YYYY-MM-DD')),
    selectedSpecialization: ko.observable(),
    selectedService: ko.observable(),
    selectedLocalization: ko.observable(),
    specializations: ko.observableArray(),
    localizations: ko.observableArray(),
    services: ko.observableArray(),
    doctor: ko.observable({}),
    doctorFilter: ko.observable(''),
    loadDoctors: function(){
        if (this == window)
            return;
        var params = {ordering: 'next_term'};
        if (this.doctorFilter() && this.doctorFilter().length > 2)
            params.name_like = this.doctorFilter();
        if (this.selectedSpecialization())
            params.specialization = this.selectedSpecialization().id;
        if (this.selectedLocalization())
            params.localization = this.selectedLocalization().id;
        if (this.dateFrom())
            params.dateFrom = this.dateFrom();
        var me = this;
        params.calendar = 1;
        $.get('/rest/doctors/', params, function(res){
            me.doctors(res.results);
        });
    },
    loadDoctorCalendar: function(doctor){
        if (doctor === undefined)
            return;
        fullCalendarModel.doctor(doctor);
        var date = doctor.first_term;
        var dt = date.substr(6,4) + '-' + date.substr(3,2) + '-' + date.substr(0,2);
        $('#calendar').fullCalendar('option', {
           minTime: doctor.terms_start.substr(0, 5),
           maxTime: doctor.terms_end.substr(0, 5),
           defaultDate: dt //defaultDate: moment(dt)
        });
        $('#calendar').fullCalendar('gotoDate', dt);
        //$('#calendar').fullCalendar('refetchEvents');
    }
};

$(document).ready(function(){
    ko.applyBindings(fullCalendarModel, $('#doctors-list')[0]);
    ko.applyBindings(fullCalendarModel, $('#calendar-filters')[0]);
    fullCalendarModel.delayedFilter = ko.pureComputed(fullCalendarModel.doctorFilter).extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 400 } }),
    fullCalendarModel.delayedFilter.subscribe(function (val) {
        fullCalendarModel.loadDoctors();
    }, this);
    fullCalendarModel.loadDoctors();
});
