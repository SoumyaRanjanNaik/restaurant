import xlwt
import os
from restaurant.settings import BASE_DIR
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Avg, Sum
from .models import *
from datetime import datetime
from django.db.models import Count, Sum


def cleaner(l):
    # list cleaner for empty entries(used in functions above)

    i = -1
    while l[i] == "":
        l.remove("")
    return l


def top_find(request):

    now = datetime.now()
    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        if start_date and end_date:
            # if both dates are present, so we have a date window. startdate>=results<=enddate
            bills = Bill.objects.filter(
                date__gte=start_date, date__lte=end_date
            ).values_list("bill_id", flat=True)
        elif start_date:
            # if only the start_date is provided. The resulted queryset will extend till today.
            bills = Bill.objects.filter(date__gte=start_date).values_list(
                "bill_id", flat=True
            )
        elif end_date:
            # queryset will contain results till the enddate
            bills = Bill.objects.filter(date__lte=end_date).values_list(
                "bill_id", flat=True
            )
        else:
            return redirect("list_bills")

    else:
        # Query to get bills of the present day.
        bills = Bill.objects.filter(date=now).values_list("bill_id", flat=True)

    bills = list(bills)
    top = (
        Kot.objects.values("dish")
        .filter(bill_id__gte=int(bills[0]), bill_id__lte=int(bills[len(bills) - 1]))
        .annotate(max=Count("dish"))
        .order_by("dish")
    )
    lst = [i["dish"] for i in top]
    return lst


def xls(bills):
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Sale")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["Bill ID", "Date", "Amount", "CGST", "SGST", "Net Amount"]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = bills.values_list(
        "bill_id", "date", "sub_total", "cgst", "sgst", "amount")
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 1:
                data = datetime.strptime(str(row[col_num]), "%Y-%m-%d").strftime(
                    "%d/%m/%Y"
                )
                ws.write(row_num, col_num, data, font_style)
            else:
                ws.write(row_num, col_num, row[col_num], font_style)

    filename = os.path.join(BASE_DIR, "sale_report.xls")
    wb.save(filename)
    return
