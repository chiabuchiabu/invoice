from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
import re


# Create your models here.
def validate_invoice_number(value):
    if not re.match(r'^[A-Z]{2}\d{8}$', value):
        raise ValidationError('發票號碼格式錯誤，應為 2 個大寫英文字母 + 8 個數字，例如 AB12345678')




class Partner(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(blank=True,null=True)
    phone=models.CharField(max_length=20,blank=True,null=True)
    partner_number=models.CharField(max_length=8,blank=True,null=True)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    INVOICE_TYPE=[
        ('AR','應收帳款'),
        ('AP','應付帳款')
    ]
    partner=models.ForeignKey(Partner,on_delete=models.CASCADE)
    invoice_type=models.CharField(max_length=2,choices=INVOICE_TYPE)
    invoice_number = models.CharField(
        max_length=10,blank=True,null=True,
        validators=[validate_invoice_number],
        unique=True,
    )
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    amount_excl_tax=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    tax_amount=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    description=models.TextField(blank=True)
    date=models.DateField()
    is_paid=models.BooleanField(default=False)
    not_deducted=models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.amount and not self.not_deducted:
            self.tax_amount = ((self.amount / Decimal('1.05')) * Decimal('0.05')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            self.amount_excl_tax = self.amount - self.tax_amount
        super().save(*args, **kwargs)
    
    def __str__(self): 
        return f"{self.id} : {self.get_invoice_type_display()} - {self.partner.name} - {self.amount}"
