from django.urls import path

from .views import *

urlpatterns = [
    path('transactions', ledger, name='transactions'),
    path('repayment/', repayment, name='repayment'),
]
