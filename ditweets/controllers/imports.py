# -*- coding: utf-8 -*-
from ditweets import cache

def gsheet_twitter():
    from openpyxl import load_workbook
    from io import BytesIO
    import requests

    r =requests.get("https://docs.google.com/spreadsheets/d/1PPypAFZXc5Kd2IzA9G8sij3ScsBYFE0rROqtaDm0mN0/export?format=xlsx&id=1PPypAFZXc5Kd2IzA9G8sij3ScsBYFE0rROqtaDm0mN0")
    f = BytesIO(r.content)
    wb = load_workbook(f)

    ws = wb[wb.sheetnames[0]]
    from collections import OrderedDict
    comptes = OrderedDict()
    for row in ws.iter_rows(min_row=1):
        if row[0].value:
            compte = row[0].value.strip()[1:]
            categorie = row[1].value.strip()
            statut = row[2].value.strip()
            if statut == u'Confirmé':
                comptes[categorie] = comptes.get(categorie,[]) + [compte]


    cache['comptes'] = comptes

    return "ok"
