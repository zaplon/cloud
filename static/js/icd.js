$(document).ready(function () {
    $('#icd-table').bootstrapTable({
        url: '/rest/icd/',
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
        columns: [{
            field: 'code',
            title: 'Kod',
            align: 'center',
            width: '10%'
        }, {
            field: 'desc',
            title: 'Opis',
            align: 'center',
        }]
    });

    $('#toolbar').find('select').change(function () {
        $table.bootstrapTable('refreshOptions', {
            exportDataType: $(this).val()
        });
    });
});
