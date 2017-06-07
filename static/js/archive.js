$(document).ready(function () {
    if ($('#archive-table').length > 0) {

        $('#search-suggestions').click(function(e){
            e.preventDefault();
            var value = $(e.target).html();
            $('.search input').val(value);
            $('#archive-table').bootstrapTable('refresh', {query: {is_table: true, limit: gabinet.pageLimit, search: value}});
        });

        $('#archive-table').bootstrapTable({
            url: '/archive/search/',
            search: true,
            queryParams: function (params) {
                params.is_table = true;
                params.limit = gabinet.pageLimit;
                return params;
            },
            responseHandler: function (res) {
                if (res.suggestions.length > 0) {
                    $('#search-suggestion-container').css('display', 'block');
                    $('#search-suggestions').html(res.suggestions[0]);
                }
                else
                    $('#search-suggestion-container').css('display', 'none');
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
                align: 'center',
                formatter: function (value, row, index) {
                    return value.first_name + ' ' + value.last_name + ' (' + value.pesel + ')';
                }
            }, {
                field: 'uploaded',
                title: 'Dodano',
                align: 'center',
                formatter: function (value) {
                    var d = new Date(value);
                    return moment(d).format('DD-MM-YYYY HH:mm');
                }
            }, {
                field: 'url',
                title: 'Dokument',
                align: 'center',
                formatter: function (value, row, index) {
                    var klass = 'fa-file-pdf-o';
                    if (row.type == 'VIDEO')
                        klass = 'fa-file-video-o';
                    return '<a href="' + value + '"<i class="fa ' + klass + '" ></a>'
                }
            }
            ]
        });

        $('#toolbar').find('select').change(function () {
            $table.bootstrapTable('refreshOptions', {
                exportDataType: $(this).val()
            });
        });
    }
    if ($('#archive').length > 0)
        $('#search-results').click(function () {
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
