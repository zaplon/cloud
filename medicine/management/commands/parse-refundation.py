from django.core.management.base import BaseCommand, CommandError
from medicine.models import Refundation, Medicine, MedicineParent
import xlrd, math


class Command(BaseCommand):
    file = 'medicine/data/leki.xls'
    source = ''

    def handle(self, *args, **options):
        # url = urllib.URLopener()
        # url.retrieve(self.source,self.file)
        m = xlrd.open_workbook(self.file, encoding_override="utf8", formatting_info=True)
        sheets = []

        xls_cols = [{'patient_price': 15, 'netto': 8, 'limit': 11, 'detal': 10, 'brutto': 9, 'substance': 1, 'ean': 4,
                     'name': 2, 'size': 3, 'group': 7, 'recommendations': 12, 'other_recommendations': 13,
                     'to_pay': 14},
                    {'patient_price': 15, 'netto': 8, 'limit': 11, 'detal': 10, 'brutto': 9, 'substance': 1, 'ean': 4,
                     'name': 2, 'size': 3, 'group': 7, 'recommendations': 12, 'other_recommendations': 13,
                     'to_pay': 14},
                    {'patient_price': 15, 'netto': 8, 'limit': 11, 'detal': 10, 'brutto': 9, 'substance': 1, 'ean': 4,
                     'name': 2, 'size': 3, 'group': 7, 'recommendations': 12, 'other_recommendations': 13,
                     'to_pay': 14},
                    {'netto': 8, 'limit': 10, 'brutto': 9, 'substance': 1, 'ean': 4, 'name': 2, 'size': 3, 'group': 7,
                     'to_pay': 12},
                    {'netto': 8, 'limit': 10, 'brutto': 9, 'substance': 1, 'ean': 4, 'name': 2, 'size': 3, 'group': 7,
                     'to_pay': 12}
                    ]

        for i in range(m.nsheets):
            s = m.sheet_by_index(i)
            sheets.append([])
            first_row = True
            for r in range(s.nrows):
                vals = s.row_values(r)
                if len(vals[1]) == 0:
                    continue
                if first_row:
                    first_row = False
                    headers = vals
                else:
                    j = 0
                    # obj = {}
                    obj = []
                    for v in vals:
                        # obj[headers[j]] = v
                        obj.append(v)
                        j = j + 1
                    sheets[i].append(obj)

        Refundation.objects.all().delete()

        i = 0
        for sheet in sheets:
            for row in sheet:
                r = Refundation()
                try:
                    if len(row[xls_cols[i]['ean']].split(',\n')) > 0:
                        row[xls_cols[i]['ean']] = row[xls_cols[i]['ean']].split(',\n')[0]
                except:
                    continue
                if 'recommendations' in xls_cols[i]:
                    if len(row[xls_cols[i]['recommendations']]) > 500:
                        row[xls_cols[i]['recommendations']] = row[xls_cols[i]['recommendations']][1:499]
                    if len(row[xls_cols[i]['other_recommendations']]) > 500:
                        row[xls_cols[i]['other_recommendations']] = row[xls_cols[i]['other_recommendations']][1:500]
                for o in xls_cols[i]:
                    print row[xls_cols[i][o]]
                    if type(row[xls_cols[i][o]]) is str:
                        setattr(r, o, row[xls_cols[i][o]].encode('utf8'))
                    else:
                        setattr(r, o, row[xls_cols[i][o]])
                    # r.o =  row[xls_cols[i][o]]

                # czy to nowy lek
                m = Medicine.objects.filter(ean=r.ean)
                if len(m) > 0:
                    m = m[0]
                    m.in_use = True
                    m.save()
                else:
                    dose = r.name.split(',')
                    dose = dose[-1]
                    p = MedicineParent.objects.create(name=r.name)
                    m = Medicine.objects.create(ean=r.ean, parent=p, size=r.size, in_use=1, refundation=1)
                r.medicine = m
                m.refundation = True
                m.save()
                r.save()
            i += 1

            # for m in Medicine.objects.all():
            #     try:
            #         Refundation.objects.get(ean = m.ean)
            #         m.refundation = True
            #     except:
            #         m.refundation = False
            #     print m.id
            #     m.save()
