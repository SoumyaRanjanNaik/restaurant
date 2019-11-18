from django.shortcuts import render, HttpResponse, redirect
from sale.services import cleaner
from stock.models import *
from datetime import datetime
from django.db.models import Avg, Sum
from ledger.models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


@login_required
def add_vendor(request):

    if request.method == "POST":
        name = request.POST.get("name").upper()
        address = request.POST.get("address")
        contact = request.POST.get("contact")

        v = Vendor(name=name, address=address, contact=contact, balance=0)
        v.save()
        context = {"msg": "Vendor " + v.name + " added successfully"}
        return render(request, "add_vendor.html", context)
    else:
        return render(request, "add_vendor.html")


@login_required
def add_item(request):

    if request.method == "POST":
        name = request.POST.get("name").upper()
        unit = request.POST.get("unit")
        category = request.POST.get("category")

        i = Item(name=name, unit=unit, quantity=0, category=category)
        i.save()
        context = {"msg": "Item " + i.name + " added successfully"}
        return render(request, "add_item.html", context)

    else:
        return render(request, "add_item.html")


@login_required
def restock(request):

    if request.method == "POST":
        vendor = Vendor.objects.get(id=request.POST.get("vendor").upper())
        items = request.POST.getlist("item")
        amounts = request.POST.getlist("amount")
        quantities = request.POST.getlist("quantity")
        amount_sum = 0
        for i in range(len(items)):
            item = Item.objects.get(id=items[i])
            s = Stock(
                item=item,
                vendor=vendor,
                quantity=int(quantities[i]),
                amount=round(float(amounts[i]), 2),
            )
            s.save()
            amount_sum += int(amounts[i])
            item.quantity += int(quantities[i])
            item.save()

        debit = float(request.POST.get("debit"))
        balance = amount_sum - debit

        t = Transaction(debit=debit, name=vendor.name)
        t.save()

        vendor.balance = vendor.balance + balance
        vendor.save(force_update=True)

        context = {
            "items": Item.objects.all(),
            "vendors": Vendor.objects.all(),
            "categories": Item.objects.all()
            .values_list("category", flat=True)
            .distinct(),
        }
        rem_date = request.POST.get("rem_date")
        if rem_date:
            vendor.reminder_date = rem_date
            vendor.save(force_update=True)
        context["msg"] = "Stock Updated"

        return render(request, "restock_form.html", context)

    else:
        context = {
            "items": Item.objects.all(),
            "vendors": Vendor.objects.all(),
            "categories": Item.objects.all()
            .values_list("category", flat=True)
            .distinct(),
        }
        return render(request, "restock_form.html", context)


@login_required
def restock_history(request):
    now = datetime.now()
    most_restock = None
    least_restock = None

    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        if start_date and end_date:
            # if both dates are present, so we have a date window. startdate>=results<=enddate
            stock = Stock.objects.filter(
                date__gte=start_date, date__lte=end_date)
        elif start_date:
            # if only the start_date is provided. The resulted queryset will extend till today.
            stock = Stock.objects.filter(date__gte=start_date)
        elif end_date:
            # queryset will contain results till the enddate
            stock = Stock.objects.filter(date__lte=end_date)
        else:
            return redirect("restock_history")

    else:
        # Query to get stock of the present day.
        stock = Stock.objects.filter(date=now)

    # if stock:
    # top = top_find(request)
    # most_restock = Stock.objects.get(dish_id=str(top[0]))
    # least_restock = Stock.objects.get(dish_id=str(top[len(top) - 1]))

    sale = stock.aggregate(Avg("amount"), Sum("amount"))
    avg = sale["amount__avg"]
    total_restock = sale["amount__sum"]

    # excel_sheet = xls(stock)

    context = {
        "stock": stock,
        "total_restock": total_restock,
        "avg": avg,
        # 'most_restock': most_restock,
        # 'least_restock': least_restock,
        # 'excel_sheet': excel_sheet
    }

    return render(request, "restock_history.html", context)


@login_required
def item_expenditure(request):
    context = {
        "items": Item.objects.all(),
    }
    if request.method == "POST":
        items = request.POST.getlist("item")
        quantities = request.POST.getlist("quantity")
        for i in range(0, len(items)):

            print(items[i], quantities[i])
            item = Item.objects.get(id=int(items[i]))
            item.quantity = item.quantity - int(quantities[i])
            item.save()
        context["msg"] = "Stock updated"
    return render(request, "item_expenditure.html", context)


@login_required
def inventory(request):
    context = {"items": Item.objects.all()}
    return render(request, "inventory.html", context)
