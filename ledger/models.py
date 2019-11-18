from django.db import models


class Transaction(models.Model):
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    debit = models.FloatField(null=True, default=0.0)
    credit = models.FloatField(null=True, default=0.0)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
