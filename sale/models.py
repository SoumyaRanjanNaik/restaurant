from django.db import models


class Dishes(models.Model):
    dish_id = models.CharField(max_length=50, primary_key=True, unique=True)
    dish_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null=True)
    half_price = models.FloatField(null=True)
    full_price = models.FloatField(null=True)
    ftype = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return str(self.dish_id) + "|" + str(self.dish_name)


class Customers(models.Model):
    name = models.CharField(max_length=100)
    balance = models.FloatField()
    reminder_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Bill(models.Model):
    bill_id = models.AutoField(unique=True, primary_key=True)
    daily_count=models.IntegerField(null=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    discount = models.FloatField(null=True)
    sub_total = models.FloatField(null=True, default=0.0)
    amount = models.FloatField(null=True)
    cgst = models.FloatField(null=True, blank=True)
    sgst = models.FloatField(null=True, blank=True)
    payment_type = models.TextField(max_length=100, default="Cash")
    order_type = models.TextField(max_length=100, default="Restaurant")
    table_no = models.CharField(null=True, max_length=20)
    staff_name = models.ForeignKey(
        "Staff", on_delete=models.CASCADE, null=True)
    cust_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.bill_id) + "|" + str(self.date)


class Kot(models.Model):
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    table = models.CharField(default="0", max_length=20)
    status = models.BooleanField(default=True)
    dish = models.ForeignKey("Dishes", on_delete=models.CASCADE)
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=1)
    bill_id = models.IntegerField(null=True)
    staff_name = models.ForeignKey(
        "Staff", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.table)


class Staff(models.Model):
    name = models.CharField(max_length=100)
    contact = models.IntegerField()

    def __str__(self):
        return str(self.name)
