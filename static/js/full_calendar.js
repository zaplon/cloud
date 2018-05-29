
var fullCalendarView = new Vue({
    el: '#calendar-controls',
    data: {
        doctors: [],
        dateFrom: moment(new Date()).format('YYYY-MM-DD'),
        selectedSpecialization: '',
        selectedService: '',
        selectedLocalization: '',
        specializations: [],
        localizations: [],
        services: [],
        service: '',
        doctor: '',
        doctorFilter: '',
    },
    watch: {
        doctorFilter: debounce(function (val) {
            this.loadDoctors();
        }, 250)},
    methods: {
        loadDoctors: function () {
            if (this == window)
                return;
            var params = {ordering: 'next_term'};
            if (this.doctorFilter && this.doctorFilter.length > 2)
                params.name_like = this.doctorFilter;
            if (this.selectedSpecialization)
                params.specialization = this.selectedSpecialization;
            if (this.selectedLocalization)
                params.localization = this.selectedLocalization;
            if (this.dateFrom)
                params.dateFrom = this.dateFrom;
            var me = this;
            params.calendar = 1;
            $.get('/rest/doctors/', params, function (res) {
                me.doctors = res.results;
            });
        },
        loadDoctorCalendar: function (doctor) {
            if (doctor === undefined)
                return;
            fullCalendarView.doctor = doctor;
            var date = doctor.first_term;
            var dt = date.substr(6, 4) + '-' + date.substr(3, 2) + '-' + date.substr(0, 2);
            $('#calendar').fullCalendar('option', {
                minTime: doctor.terms_start.substr(0, 5),
                maxTime: doctor.terms_end.substr(0, 5),
                defaultDate: dt //defaultDate: moment(dt)
            });
            var cd = $('#calendar').fullCalendar('getDate');
            if ($.isArray(cd._i) || cd._i == moment(dt)._i)
                $('#calendar').fullCalendar('refetchEvents');
            else
                $('#calendar').fullCalendar('gotoDate', dt);
        }
    }
});

$(document).ready(function () {
    // fullCalendarModel.delayedFilter = ko.pureComputed(fullCalendarModel.doctorFilter).extend({
    //     rateLimit: {
    //         method: "notifyWhenChangesStop",
    //         timeout: 400
    //     }
    // }),
    // fullCalendarModel.delayedFilter.subscribe(function (val) {
    //     fullCalendarModel.loadDoctors();
    // }, this);
    fullCalendarView.loadDoctors();
});

