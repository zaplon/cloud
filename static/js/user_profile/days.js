dayNames = ['poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela'];
var day = function (dayIndex) {
    return {
        start: '09:00', end: '17:00', break_start: null, break_end: null, dayName: dayNames[dayIndex - 1],
        dayIndex: dayIndex - 1, hasBreak: ko.observable(false), dayChecked: ko.observable(dayIndex > 5 ? false : true)
    }
};

var dayError = function(){
    return {start: false, end: false, break_start: false, break_end: false};
};

$(document).ready(function () {
    if (gabinet.doctor.working_hours.length > 0)
        var days = gabinet.doctor.working_hours;
    else
        var days = [day(1), day(2), day(3), day(4), day(5), day(6), day(7)];
    var viewModel = {
        days: ko.observableArray(days),
        errors: ko.observableArray([dayError(1), dayError(2), dayError(3), dayError(4), dayError(5), dayError(6), dayError(7)]),
        dayNames: dayNames,
        saveDays: function () {
            $.post('/profile/settings/', {days: ko.toJSON(viewModel.days), tab: 1}).success(function (res) {
                if (res.success){
                        window.location.pathname = '/';
                        notie.alert('success', 'Dane zapisano poprawnie', 3);
                    }
                    else {
                        viewModel.errors = res.errors;
                    }
            });
        }
    };
    ko.applyBindings(viewModel, $('#settings-modal')[0]);
});
