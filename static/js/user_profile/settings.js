dayNames = ['poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela'];
var day = function(dayIndex){
    return {start: '09:00', end: '17:00', break_start: null, break_end: null, dayName: dayNames[dayIndex-1],
        dayIndex: dayIndex - 1, hasBreak: ko.observable(false), dayChecked: ko.observable(dayIndex > 5 ? false: true)}
};

$(document).ready(function (){
    var viewModel = {
        days: ko.observableArray([day(1), day(2), day(3), day(4), day(5), day(6), day(7)]),
        dayNames: dayNames,
        errors: ko.observableArray([]),
        saveDays: function(){
            $.post('/profile/settings/', {days: JSON.stringify(viewModel.days()), tab:1}).success(function(res){
                if (res.success)
                    notie.alert('success', 'Dane zapisano poprawnie', 3);
                else {
                    viewModel.errors = res.errors;
                }
            });
        }
    };
    ko.applyBindings(viewModel);
});