# -*- coding: utf-8 -*-

def twitter_gsheet():
    from openpyxl import load_workbook
    from io import BytesIO
    import requests

    r =requests.get("https://docs.google.com/spreadsheets/d/1PPypAFZXc5Kd2IzA9G8sij3ScsBYFE0rROqtaDm0mN0/export?format=xlsx&id=1PPypAFZXc5Kd2IzA9G8sij3ScsBYFE0rROqtaDm0mN0")
    f = BytesIO(r.content)
    wb = load_workbook(f)

    ws = wb[wb.sheetnames[0]]
    comptes = {}
    for row in ws.iter_rows(min_row=1):
        if row[0].value:
            compte = row[0].value[1:]
            categorie = row[1].value
            statut = row[2].value
            if statut == u'Confirmé':
                print(compte,categorie,statut)

    return "ok"
