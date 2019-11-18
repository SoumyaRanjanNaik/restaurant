from django.shortcuts import render, redirect
from .models import *
from stock.models import Vendor
from sale.models import Customers
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


@staff_member_required
def ledger(request):
    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        name = request.POST.get("name")

        if start_date and end_date and name:
            transactions = Transaction.objects.filter(date__gte=start_date,
                                                      date__lte=end_date,
                                                      name__iexact=name)

        elif start_date and end_date:
            transactions = Transaction.objects.filter(date__gte=start_date,
                                                      date__lte=end_date)

        elif start_date and name:
            transactions = Transaction.objects.filter(date__gte=start_date,
                                                      name__iexact=name)

        elif end_date and name:
            transactions = Transaction.objects.filter(date__lte=end_date,
                                                      name__iexact=name)

        elif start_date:
            transactions = Transaction.objects.filter(date__gte=start_date)

        elif end_date:
            transactions = Transaction.objects.filter(date__lte=end_date)

        elif name:
            transactions = Transaction.objects.filter(name__iexact=name)

        else:
            return redirect('transactions')

    else:
        now = datetime.now()
        transactions = Transaction.objects.filter(date__gte=now)

    net_debit = round(sum(transactions.values_list('debit', flat=True)), 2)
    net_credit = round(sum(transactions.values_list('credit', flat=True)), 2)
    net = net_credit - net_debit
    if net > 0:
        net_type = "PROFIT"
        color = "green"
    else:
        net_type = "LOSS"
        color = "red"
    names = Transaction.objects.all().values_list('name', flat=True).distinct()
    context = {
        'transactions': transactions,
        'names': names,
        'net': net,
        'net_type': net_type,
        'color': color,
        'net_credit': net_credit,
        'net_debit': net_debit
    }
    return render(request, 'ledger.html', context)


@login_required
def repayment(request):
    context = {}
    if request.method == "POST":
        print(request.POST)
        rem_date = request.POST.get('rem_date')
        id_type = request.POST.get("id_type")
        amt = int(request.POST.get('amt'))
        id = request.POST.get('id')
        if id_type == "vendor":
            v = Vendor.objects.get(id=id)
            v.balance = v.balance - amt
            v.save()
            t = Transaction(name=v.name, debit=amt)
            t.save()
            context['msg'] = "vendor payment saved"
            rem_date = request.POST.get('rem_date')
            if rem_date is not None:
                v.reminder_date = rem_date
                v.save(force_update=True)
                context['msg2'] = "reminder added successfully"
        else:
            c = Customers.objects.get(id=id)
            c.balance = c.balance - amt
            c.save()
            t = Transaction(name=c.name, credit=amt)
            t.save()
            context['msg'] = "customer payment saved"
            rem_date = request.POST.get('rem_date')
            if rem_date is not None:
                c.reminder_date = rem_date
                c.save(force_update=True)
                context['msg2'] = "reminder added successfully"
        context['vendors'] = Vendor.objects.all()
        context['customers'] = Customers.objects.all()
        return render(request, 'repayment.html', context)
    else:
        context['vendors'] = Vendor.objects.all()
        context['customers'] = Customers.objects.all()
        return render(request, 'repayment.html', context)
