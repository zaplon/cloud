dayNames = ['poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela'];
var day = function (dayIndex) {
    return {
        start: '09:00', end: '17:00', break_start: null, break_end: null, dayName: dayNames[dayIndex - 1],
        dayIndex: dayIndex - 1, hasBreak: ko.observable(false), dayChecked: ko.observable(dayIndex > 5 ? false : true)
    }
};

var dayError = function(){
    return {start: false, end: false, break_start: false, break_end: false};
}

var ready = function () {
    var viewModel = {
        days: ko.observableArray([day(1), day(2), day(3), day(4), day(5), day(6), day(7)]),
        errors: ko.observableArray([dayError(1), dayError(2), dayError(3), dayError(4), dayError(5), dayError(6), dayError(7)]),
        dayNames: dayNames,
        saveSettings: function (){
            if ($('#profile').is(':visible'))
                viewModel.saveProfile();
            else
                viewModel.saveDays();
        },
        saveDays: function () {
            $.post('/profile/settings/', {days: JSON.stringify(viewModel.days()), tab: 1}).success(function (res) {
                if (res.success)
                    if (window.location.pathname.indexOf('setup') > -1) {
                        window.location.pathname = '/';
                        notie.alert('success', 'Dane zapisano poprawnie', 3);
                    }
                    else {
                        viewModel.errors = res.errors;
                    }
            });
        },
        saveProfile: function () {
            $.ajax({
                data: {data: $('#profile form').serialize(), class: 'DoctorForm', module: 'user_profile.forms', user: true},
                url: '/get-form/',
                type: 'POST',
                success: function (res) {
                    if (!res.success) {
                        // Here we replace the form, for the
                        $('#profile form').replaceWith(res.form_html);
                    }
                    else {
                        if (window.location.pathname.indexOf('setup') > -1)
                            window.location.pathname = '/';
                        $('#settings-modal').modal('hide');
                        //notie.alert('success', 'Dane zapisano poprawnie', 3);
                        // Here you can show the user a success message or do whatever you need
                        //$(example_form).find('.success-message').show();
                    }
                }
            });
        }
    };
    ko.applyBindings(viewModel, $('#settings-modal')[0]);
};

