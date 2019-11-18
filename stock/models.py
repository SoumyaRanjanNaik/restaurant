from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    contact = models.CharField(max_length=10)
    balance = models.FloatField(default=0)
    reminder_date = models.DateField(null=True)

    def __str__(self):
        return str(self.name)


class Stock(models.Model):
    date = models.DateField(auto_now_add=True)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    vendor = models.ForeignKey("Vendor", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.FloatField()

    def __str__(self):
        return str(self.item.name)


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=10)
    category = models.CharField(max_length=50, null=True)

    def __str__(self):
        return str(self.name)
