from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model=Invoice
        exclude = ['amount_excl_tax', 'tax_amount']
        labels={
            'partner':'partner(廠商)',
            'invoice_type':'invoice_type(發票類型)',
            'invoice_number':'invoice_number(發票號碼)',
            'amount':'amount(金額)',
            'description':'description(描述)',
            'date':'date(發票日期)',
            'is_paid':'is_paid(是否付款)',
            'not_deducted':'不可扣抵'

        }