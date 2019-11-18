from django.contrib import admin
from django.urls import path

from stock.views import *

urlpatterns = [
    path('add_vendor/', add_vendor, name='add_vendor'),
    path('add_item/', add_item, name='add_item'),
    path('restock/', restock, name='restock'),
    path('restock_history/', restock_history, name='restock_history'),
    path('item_expenditure', item_expenditure, name='item_expenditure'),
    path('inventory', inventory, name='inventory')
]
