$(document).ready(function () {
    $('#patients-table').bootstrapTable({
        url: '/rest/patients/',
        search: true,
        queryParams: function (params) {
            params.is_table = true;
            params.limit = gabinet.pageLimit;
            return params;
        },
        responseHandler: function (res) {
            var res = gabinet.transformTableResponse(res);

            console.log(res);
            return res;
        },
        sidePagination: 'server',
        showFooter: false,
        pagination: true,
        idField: 'code',
        Locale: 'pl-PL',
        showExport: true,
        showRefresh: true,
        showToggle: true,
        showColumns: true,
        toolbar: '#toolbar',
        pageList: [10, 25],
        iconsPrefix: 'font-icon',
        icons: {
            paginationSwitchDown: 'font-icon-arrow-square-down',
            paginationSwitchUp: 'font-icon-arrow-square-down up',
            refresh: 'font-icon-refresh',
            toggle: 'font-icon-list-square',
            columns: 'font-icon-list-rotate',
            export: 'font-icon-download',
            detailOpen: 'font-icon-plus',
            detailClose: 'font-icon-minus-1'
        },
        paginationPreText: '<i class="font-icon font-icon-arrow-left"></i>',
        paginationNextText: '<i class="font-icon font-icon-arrow-right"></i>',
        columns: [
            {
                field: 'state',
                checkbox: true,
                align: 'center',
                valign: 'middle'
            },
            {
                field: 'pesel',
                title: 'Pesel',
                align: 'center',
                formatter: function (value, row, index) {
                    if (!value)
                        value = 'Brak';
                    return '<a href="/profile/patients/' + row.id + '/">' + value + '</a>';
                }
            },
            {
                field: 'last_name',
                title: 'Nazwisko',
                align: 'center'
            }, {
                field: 'first_name',
                title: 'Imię',
                align: 'center'
            }]
    });

    $('#toolbar').find('select').change(function () {
        $table.bootstrapTable('refreshOptions', {
            exportDataType: $(this).val()
        });
    });

    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row.id
        });
    }

    var $table = $('#patients-table');
    var $remove = $('#remove');
    $table.on('check.bs.table uncheck.bs.table ' +
        'check-all.bs.table uncheck-all.bs.table', function () {
        $remove.prop('disabled', !$table.bootstrapTable('getSelections').length);
        // save your data, here just save the current page
        // push or splice the selections if you want to save all data selections
    });
    $remove.click(function () {
        var selections = getIdSelections();
        selections.forEach(function (s) {
            $.ajax({
                type: 'DELETE',
                url: '/rest/patients/' + s + '/',
                success: function () {
                    $table.bootstrapTable('remove', {field: 'id', values: [s]});
                },
                error: function () {
                    notie.alert(2, 'Nie wszystkie rekordy udało się usunąć')
                }
            })
        })
    });

});
