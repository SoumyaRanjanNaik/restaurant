from django.contrib import admin
from .models import *

admin.site.register([Dishes, Bill, Kot, Staff, Customers])
