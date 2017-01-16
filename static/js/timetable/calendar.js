var calendar = {
    saveTerm: function (calEvent) {
        if ($('#edit-form form').length > 0)
            var data = $('#edit-form form').serializeArray();
        else {
            dr = calEvent.doctor.split('/');
            dr = dr[dr.length-2];
            data = [{name: 'status', value: calEvent.status}, {name: 'doctor', value: dr}];
        }
        data.push({name: 'datetime', value: calEvent.start._i.substr(0, calEvent.start._i.length - 9)});
        data.push({name: 'id', value: calEvent.id});
        $.post('/get-form/', {
            module: 'timetable.forms', class: 'TermForm',
            data: JSON.stringify(data)
        }, function (res) {
            if (res.success) {
                $('.fc-popover.click').remove();
                $('#calendar').fullCalendar('refetchEvents');
            } else
                $('#edit-form form').html(res.form_html);
        });
    }
};


$(document).ready(function () {

    /* ==========================================================================
     Fullcalendar
     ========================================================================== */

    var viewModel = {
        nextVisits: ko.observableArray(),
        formatDate: function (date) {
            var d = new Date(date);
            return d.toLocaleString();
        }
    };
    $.getJSON("/rest/terms/?next_terms=1", function (data) {
        viewModel.nextVisits(data);
    });
    ko.applyBindings(viewModel);

    $('#calendar').fullCalendar({
        locale: 'pl',
        defaultView: 'agendaWeek',
        slotDuration: '00:15:00',
        displayEventTime: false,
        minTime: gabinet.doctor.terms_start.substr(0, 5),
        maxTime: gabinet.doctor.terms_end.substr(0, 5),
        header: {
            left: '',
            center: 'prev, title, next',
            right: 'today agendaDay,agendaTwoDay,agendaWeek,month'
        },
        buttonIcons: {
            prev: 'font-icon font-icon-arrow-left',
            next: 'font-icon font-icon-arrow-right',
            prevYear: 'font-icon font-icon-arrow-left',
            nextYear: 'font-icon font-icon-arrow-right'
        },
        editable: true,
        selectable: true,
        eventLimit: true, // allow "more" link when too many events
        events: {
            url: '/rest/terms/',
            type: 'GET',
            data: {},
            error: function () {
                alert('Wystąpił błąd przy pobieraniu danych!');
            }
        },
        viewRender: function (view, element) {
            // При переключении вида инициализируем нестандартный скролл
            if (!("ontouchstart" in document.documentElement)) {
                $('.fc-scroller').jScrollPane({
                    autoReinitialise: true,
                    autoReinitialiseDelay: 100
                });
            }

            $('.fc-popover.click').remove();
        },
        eventDrop: function (event, delta, revertFunc, jsEvent, ui, view) {
            calendar.saveTerm(event);
        },
        eventDragStart: function(){
            $('.fc-popover.click').remove();
        },
        eventClick: function (calEvent, jsEvent, view) {

            var eventEl = $(this);

            // Add and remove event border class
            if (!$(this).hasClass('event-clicked')) {
                $('.fc-event').removeClass('event-clicked');

                $(this).addClass('event-clicked');
            }

            // Add popover
            $('body').append(
                '<div class="fc-popover click">' +
                '<div class="fc-header">' +
                moment(calEvent.start).format('dddd • D') +
                '<button type="button" class="cl"><i class="font-icon-close-2"></i></button>' +
                '</div>' +

                '<div class="fc-body main-screen">' +
                '<p>' +
                moment(calEvent.start).format('dddd, D YYYY, hh:mma') +
                '</p>' +
                (calEvent.status != 'FREE' ?
                '<p class="color-blue-grey"><a href="/visit/' + calEvent.id + '">' + calEvent.title + '</a></p>' :
                '<p class="color-blue-grey">' + calEvent.title + '</p>')
                +
                '<ul class="actions">' +
                '<li><a href="#">Szczegóły</a></li>' +
                '<li><a href="#" class="fc-event-action-edit">Edytuj termin</a></li>' +
                (calEvent.status == 'PENDING' ?
                '<li><a href="#" class="fc-event-action-remove">Anuluj termin</a></li>' : '') +
                '</ul>' +
                '</div>' +
                (calEvent.status == 'PENDING' ?
                    ('<div class="fc-body remove-confirm">' +
                    '<p>Czy jesteś pewien, że chcesz anulować wizytę?</p>' +
                    '<div class="text-center">' +
                    '<button type="button" class="btn btn-rounded btn-sm">Tak</button>' +
                    '<button type="button" class="btn btn-rounded btn-sm btn-default remove-popover">Nie</button>' +
                    '</div>' +
                    '</div>') : '' ) +

                '<div class="fc-body edit-event"><div id="edit-term"><div id="edit-form"></div>' +
                '<div class="text-center">' +
                '<button id="save-term" type="button" class="btn btn-rounded btn-sm">Zapisz</button>' +
                '<button type="button" class="btn btn-rounded btn-sm btn-default remove-popover">Anuluj</button>' +
                '</div></div>' +
                '<div style="display:none;" id="edit-patient"><div id="edit-patient-form"></div>' +
                '<div class="text-center">' +
                '<button type="button" id="save-patient" class="btn btn-rounded btn-sm">Zapisz</button>' +
                '<button type="button" id="cancel-patient" class="btn btn-rounded btn-sm btn-default remove-popover">Anuluj</button>' +
                '</div></div>' +
                '</div>' +
                '</div>'
            );

            // Datepicker init
            $('.fc-popover.click .datetimepicker').datetimepicker({
                widgetPositioning: {
                    horizontal: 'right'
                },
                locale: 'pl'
            });

            $('.fc-popover.click .datetimepicker-2').datetimepicker({
                widgetPositioning: {
                    horizontal: 'right'
                },
                format: 'LT',
                locale: 'pl'
            });


            // Position popover
            function posPopover() {
                $('.fc-popover.click').css({
                    left: eventEl.offset().left + eventEl.outerWidth() / 2,
                    top: eventEl.offset().top + eventEl.outerHeight()
                });
            }

            posPopover();

            $('.fc-scroller, .calendar-page-content, body').scroll(function () {
                posPopover();
            });

            $(window).resize(function () {
                posPopover();
            });


            // Remove old popover
            if ($('.fc-popover.click').length > 1) {
                for (var i = 0; i < ($('.fc-popover.click').length - 1); i++) {
                    $('.fc-popover.click').eq(i).remove();
                }
            }

            // Close buttons
            $('.fc-popover.click .cl, .fc-popover.click .remove-popover').click(function () {
                $('.fc-popover.click').remove();
                $('.fc-event').removeClass('event-clicked');
            });

        }
    });


    /* ==========================================================================
     Side datepicker
     ========================================================================== */

    $('#side-datetimepicker').datetimepicker({
        inline: true,
        format: 'DD/MM/YYYY',
        locale: 'pl'
    });

    /* ========================================================================== */

});


/* ==========================================================================
 Calendar page grid
 ========================================================================== */

(function ($, viewport) {
    $(document).ready(function () {

        if (viewport.is('>=lg')) {
            $('.calendar-page-content, .calendar-page-side').matchHeight();
        }

        // Execute code each time window size changes
        $(window).resize(
            viewport.changed(function () {
                if (viewport.is('<lg')) {
                    $('.calendar-page-content, .calendar-page-side').matchHeight({remove: true});
                }
            })
        );

        $('.day').click(function (e) {
            $('#calendar').fullCalendar('gotoDate', new Date($(e.target).attr('data-day')));
            $('#calendar').fullCalendar('refetchEvents');
        });
    });
})(jQuery, ResponsiveBootstrapToolkit);

