from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Avg, Sum
from .models import *
from stock.models import Vendor
from .services import cleaner, top_find, xls
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from restaurant.settings import BASE_DIR
from datetime import datetime
import os
from ledger.models import *


@login_required
def index(request):
    context = {}
    today = datetime.now()
    context["cust_reminders"] = Customers.objects.filter(
        reminder_date__lte=today)
    context["cust_untracked"] = Customers.objects.filter(
        reminder_date__isnull=True)
    context["vend_reminders"] = Vendor.objects.filter(reminder_date__lte=today)
    context["vend_untracked"] = Vendor.objects.filter(
        reminder_date__isnull=True)
    return render(request, "dashboard.html", context)


@login_required
def list_bills(request):
    now = datetime.now()
    best_dish = None
    worst_dish = None

    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        if start_date and end_date:
            # if both dates are present, so we have a date window. startdate>=results<=enddate
            bills = Bill.objects.filter(date__gte=start_date,
                                        date__lte=end_date)
        elif start_date:
            # if only the start_date is provided. The resulted queryset will extend till today.
            bills = Bill.objects.filter(date__gte=start_date)
        elif end_date:
            # queryset will contain results till the enddate
            bills = Bill.objects.filter(date__lte=end_date)
        else:
            return redirect("bills")

    else:
        # Query to get bills of the present day.
        bills = Bill.objects.filter(date=now)

    if bills:
        top = top_find(request)
        try:
            best_dish = Dishes.objects.get(dish_id=str(top[0]))
            worst_dish = Dishes.objects.get(dish_id=str(top[len(top) - 1]))
        except:
            pass

    sale = bills.aggregate(Avg("amount"), Sum("amount"))
    avg = sale["amount__avg"]
    total_sale = sale["amount__sum"]

    if avg and total_sale:
        avg = round(avg, 2)
        total_sale = round(total_sale, 2)

    excel_sheet = xls(bills)

    context = {
        "bills": bills,
        "total_sale": total_sale,
        "avg": avg,
        "best_dish": best_dish,
        "worst_dish": worst_dish,
        "excel_sheet": excel_sheet,
    }

    return render(request, "billing_history.html", context)


@login_required
def generate_bill(request, bill_id):
    bill = Bill.objects.get(bill_id=bill_id)
    dishes = Kot.objects.filter(bill_id=bill.bill_id)
    context = {"bill": bill, "dishes": dishes}
    return render(request, "bill.html", context)


@login_required
def bill_form(request):
    # sale and bill database entry
    context = {}
    if request.method == "POST":
        discount = request.POST.get("discount")
        payment_type = request.POST.get("payment_type")
        order_type = request.POST.get("order_type")
        table_no = request.POST.get("table_no")
        amt_paid = request.POST.get("amt_paid")
        staff_name = request.POST.get("staff")
        cust_name = request.POST.get("cust").upper()

        cgst = request.POST.get("cgst")
        sgst = request.POST.get("sgst")
        cgst = float(cgst) / 100
        sgst = float(sgst) / 100

        last_bill=Bill.objects.last()
        if last_bill.date==datetime.now():
            try:
                daily_count=last_bill.daily_count+1
            except:
                daily_count=1
        else:
            daily_count=1

        bill = Bill(
            daily_count=daily_count,
            discount=discount,
            amount=0,
            cgst=cgst,
            sgst=sgst,
            payment_type=payment_type,
            order_type=order_type,
            table_no=table_no,
            staff_name=Staff.objects.get(name=staff_name),
            cust_name=cust_name,
        )
        bill.save()
        b_id = bill.pk
        kots = Kot.objects.filter(table=table_no, status=True)
        amt = 0
        for i in kots:
            amt = amt + (i.price * i.quantity)
            amt = round(float(amt),2)
            i.bill_id = b_id
            i.status = False
            i.save()

        bill.sub_total = amt
        bill.cgst = round(amt * cgst, 2)
        bill.sgst = round(amt * sgst, 2)
        bill.amount = round(float(amt + bill.cgst + bill.sgst - float(discount)),2)
        bill.save()
        rem_date = None
        if payment_type == "credit":
            bal = bill.amount - int(amt_paid)
            c = Customers(name=cust_name, balance=bal)
            c.save()
            t = Transaction(name=cust_name, credit=int(amt_paid))
            rem_date = request.POST.get("rem_date")

        if rem_date:
            c.reminder_date = rem_date
            c.save(force_update=True)
            context["msg"] = "Reminder added successfully"
        else:
            t = Transaction(name=cust_name, credit=amt)
        t.save()

        return redirect("generate_bill", bill_id=b_id)

    else:
        table_nos = (Kot.objects.filter(status=True).values_list(
            "table", flat=True).distinct())
        context = {
            "dishes": Dishes.objects.all(),
            "table_nos": table_nos,
            "staff_list": Staff.objects.all(),
        }
        return render(request, "bill_form.html", context)


@login_required
def dish_form(request):
    msg = None

    if request.method == "POST":
        dish_id = request.POST.get("id").upper()
        dish_name = request.POST.get("name").upper()
        half_price = request.POST.get("hp")
        full_price = request.POST.get("fp")
        category = request.POST.get("category")
        ftype = request.POST.get("ftype")
        d = Dishes(
            dish_id=dish_id,
            category=category,
            dish_name=dish_name,
            half_price=half_price,
            full_price=full_price,
            ftype=ftype,
        )
        d.save()

        msg = dish_name + " is created with dish ID:" + dish_id

    dishes = Dishes.objects.all()
    context = {"msg": msg, "dishes": dishes}
    return render(request, "dish_form.html", context)


@login_required
def menu(request):
    if request.method == "POST":
        ftype = request.POST.get("ftype")
        category = request.POST.get("category")
        context = {}
        if ftype == "all" and category == "all":
            dishes = Dishes.objects.all()
            context = {"dishes": dishes}
        elif ftype != "all" and category == "all":
            dishes = Dishes.objects.filter(ftype=ftype)
            context = {"dishes": dishes}
        elif ftype == "all" and category != "all":
            dishes = Dishes.objects.filter(category=category)
            context = {"dishes": dishes}
        else:
            dishes = Dishes.objects.filter(ftype=ftype, category=category)
            context = {"dishes": dishes}
        context["category"] = dishes.values_list(
            "category", flat=True).distinct()
        return render(request, "menu_list.html", context)
    else:
        dishes = Dishes.objects.all()
        context = {"dishes": dishes}
        context["category"] = dishes.values_list(
            "category", flat=True).distinct()
        return render(request, "menu_list.html", context)


@staff_member_required
def xls_report(request):
    filename = os.path.join(BASE_DIR, "sale_report.xls")
    response = HttpResponse(open(filename, "rb").read())
    response["Content-Disposition"] = 'attachment; filename="sale_report.xls"'
    return response


@login_required
def kot_form(request):
    if request.method == "POST":
        dishes_raw = cleaner(request.POST.getlist("dish"))
        quantity = cleaner(request.POST.getlist("quantity"))
        price = cleaner(request.POST.getlist("price"))
        order_type = request.POST.get("order_type")
        table_no = str(request.POST.get("table_no"))
        staff_name = request.POST.get("staff")

        dishes = [d.split(sep=" : ")[0] for d in dishes_raw]

        category = []

        for i in range(0, len(dishes)):
            j = i + 1
            while j < len(dishes):
                if dishes[i] == dishes[j] and price[i] == price[j]:
                    q = int(quantity[i])
                    quantity[i] = q + int(quantity[j])
                    dishes.pop(j)
                    quantity.pop(j)
                    price.pop(j)
                else:
                    j += 1

        dish_names = []
        for i in range(len(dishes)):
            try:
                dish = Dishes.objects.get(dish_id=dishes[i])
            except:
                context = {
                    "tables": Kot.objects.filter(status=True),
                    "msg": "The dish ID-" + dishes[i] + " is wrong",
                    "dishes": Dishes.objects.all(),
                    "staff_list": Staff.objects.all()
                }
                return render(request, "kot_form.html", context)
            dish_names.append(dish.dish_name)

            if price[i] == "half":
                cost = dish.half_price
            else:
                cost = dish.full_price

            try:
                k = Kot.objects.get(
                    table=table_no,
                    status=True,
                    dish=dish,
                    price=cost,
                    staff_name=Staff.objects.get(name=staff_name),
                )
                k.quantity = int(k.quantity) + int(quantity[i])
            except:
                k = Kot(
                    table=table_no,
                    dish=dish,
                    price=cost,
                    quantity=quantity[i],
                    staff_name=Staff.objects.get(name=staff_name),
                )
                category.append(dish.category)
            k.save()

        items = zip(dish_names, price, quantity, category)
        context = {"items": items, "table": table_no, "staff": staff_name}

        return render(request, "kot.html", context)

    else:
        context = {
            "dishes": Dishes.objects.all(),
            "staff_list": Staff.objects.all()
        }
        return render(request, "kot_form.html", context)


@login_required
def list_kot(request):
    now = datetime.now()

    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        if start_date and end_date:
            # if both dates are present, so we have a date window. startdate>=results<=enddate
            bills_old = Kot.objects.filter(date__gte=start_date,
                                           date__lte=end_date,
                                           status=False).order_by("bill_id")
        elif start_date:
            # if only the start_date is provided. The resulted queryset will extend till today.
            bills_old = Kot.objects.filter(date__gte=start_date,
                                           status=False).order_by("bill_id")

        elif end_date:
            # queryset will contain results till the enddate
            bills_old = Kot.objects.filter(date__lte=end_date,
                                           status=False).order_by("bill_id")
        else:
            return redirect("list_kot")

    else:
        # Query to get bills of the present day.
        bills_old = Kot.objects.filter(date=now,
                                       status=False).order_by("bill_id")

    bills = Kot.objects.filter(date=now, status=True).order_by("table")
    context = {
        "bills": bills,
        "bills_old": bills_old,
    }

    return render(request, "kot_history.html", context)
