from django.db import models

# Create your models here.


class Sale(models.Model):
    factnum = models.CharField(max_length=1000, unique=True)
    dat = models.DateField()  # the date of sale
    total = models.DecimalField(max_digits=22, decimal_places=2)
    kname = models.CharField(max_length=1000)  # customer name
    tel = models.CharField(max_length=30)
    address = models.TextField()

    def __str__(self):
        return f"{self.kname} - {self.factnum}"



class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200,default='')
    nahveh = models.CharField(max_length=300,default='')
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField()

    total_price = models.BigIntegerField()

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    food_name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    quantity = models.IntegerField()
    total = models.BigIntegerField()