$(document).ready(function () {
    if ($('#archive-table').length > 0) {
        $('#archive-table').bootstrapTable({
            url: '/archive/search/',
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
                field: 'name',
                title: 'Nazwa',
                align: 'center'
            }, {
                field: 'patient',
                title: 'Osoba',
                align: 'center'
            }, {
                field: 'pesel',
                title: 'Pesel',
                align: 'center'
            },  {
                field: 'uploaded',
                title: 'Dodano',
                align: 'center'
            }]
        });

        $('#toolbar').find('select').change(function () {
            $table.bootstrapTable('refreshOptions', {
                exportDataType: $(this).val()
            });
        });
    }
    if ($('#archive').length > 0)
        $('#search-results').click(function(){
            archive.getArchive($('input[name="pesel"]').val());
        })

});


var archive = {
    getDocument: function (id, title) {
        $.get('/rest/results/' + id, {}, function (res) {
            gabinet.showPdf(res, title);
        });
    },
    getArchive: function (pesel) {
        var me = archive;
        $.get('/rest/results/', {pesel: pesel}, function (res) {
            function adjust(node) {
                if (node.children) {
                    node.icon = 'fa fa-folder-o';
                    node.children.forEach(function (n) {
                        adjust(n);
                    });
                }
                else
                    node.icon = 'fa fa-file-pdf-o';
            }

            res.forEach(function (r) {
                adjust(r);
            });
            $('#archive').on('changed.jstree', function (e, data) {
                me.getDocument(data.selected[0], data.node.text);
            }).jstree({core: {data: res, multiple: false}});
        })
    }
}
