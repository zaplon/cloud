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
                    if (window.location.pathname.indexOf('setup') > -1)
                        window.location.pathname = '/';
                    notie.alert('success', 'Dane zapisano poprawnie', 3);
                else {
                    viewModel.errors = res.errors;
                }
            });
        },
        saveProfile: function(){
            $.ajax({
                data: $('profile-form').serialize(),
                url: '/profile/settings/',
                type: 'POST',
                success: function(res){
                    if (!(res['success'])) {
                        // Here we replace the form, for the
                        $('profile-form').replaceWith(res['form_html']);
                    }
                    else {
                        if (window.location.pathname.indexOf('setup') > -1)
                            window.location.pathname = '/';
                        notie.alert('success', 'Dane zapisano poprawnie', 3);
                        // Here you can show the user a success message or do whatever you need
                        //$(example_form).find('.success-message').show();
                    }
                }
    };
    ko.applyBindings(viewModel);
});
