from django.contrib import admin
from django.urls import path

from .views import list_bills, generate_bill, bill_form, dish_form, menu, xls_report, kot_form, list_kot

urlpatterns = [
    path('bill/<int:bill_id>', generate_bill, name='generate_bill'),
    path('bills', list_bills, name="bills"),
    path('new_bill', bill_form, name='bill_form'),
    path('new_dish', dish_form, name='dish_form'),
    path('menu', menu, name='menu'),
    path('xls_report', xls_report, name='xls_report'),
    path('kot_form/', kot_form, name='kot_form'),
    path('list_kot/', list_kot, name='list_kot'),
]
