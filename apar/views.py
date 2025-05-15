from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,redirect
from .forms import InvoiceForm
from .models import Invoice,Partner
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Sum
import csv


# Create your views here.
def index(request):
    return render(request,'apar/index.html')


def create_invoice(request):
    if request.method=='POST':
        form=InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'成功新增發票')
            return redirect('create_invoice')
    else:
        form=InvoiceForm()
    return render(request,'apar/create_invoice.html',{'form':form})


def invoice_list(request):
    invoices=Invoice.objects.all()
    paginator=Paginator(invoices,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render(request,'apar/invoice_list.html',{
        'invoices':page_obj,
        'page_obj':page_obj
    })

def partner_list(request):
    if request.method=='POST':
        partner=request.POST.get('partner')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        partner_number=request.POST.get('partner_number')
        Partner.objects.create(name=partner,phone=phone,email=email,partner_number=partner_number)
        messages.success(request, '成功新增廠商')
        return HttpResponseRedirect(reverse('partner_list'))
    else:
        return render(request,'apar/partner_list_add.html',{
    })

def payment_status(request, invoice_id):
    invoice=Invoice.objects.get(id=invoice_id)
    if request.method=='POST':
        invoice.is_paid= not invoice.is_paid
        invoice.save()
        messages.success(request,'成功更新付款狀態')

    next_url=request.GET.get('next','invoice_list')
    print('GET next:', request.GET.get('next'))
    return redirect(next_url)

def filter_date(request):
    start_date=request.GET.get('start_date')
    end_date=request.GET.get('end_date')
    if start_date and end_date:
        invoices=Invoice.objects.filter(date__range=[start_date,end_date]).order_by('date')
        total_ar_tax=invoices.filter(invoice_type='AR').aggregate(total_ar_tax=Sum('tax_amount'))['total_ar_tax'] or 0
        total_ap_tax=invoices.filter(invoice_type='AP').aggregate(total_ap_tax=Sum('tax_amount'))['total_ap_tax'] or 0
        tax=total_ar_tax-total_ap_tax
        if tax>0:
            tax_label = '應納稅額'
        elif tax<0:
            tax_label = '扣抵稅額'    
        else:
            tax_label = '無稅額'    
        taxabs=abs(tax)
        return render(request,'apar/invoice_list_filter.html',{
            'invoices':invoices,
            'total_ar_tax':total_ar_tax,
            'total_ap_tax':total_ap_tax,
            'tax_label':tax_label,
            'tax':taxabs,
            'start_date':start_date,
            'end_date':end_date
        }) 
    else:
        return redirect('invoice_list')

def export_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    total_ar_tax=request.GET.get('total_ar_tax')
    total_ap_tax=request.GET.get('total_ap_tax')
    tax_label=request.GET.get('tax_label')
    tax=request.GET.get('tax')
    
    if start_date and end_date:
        invoices = Invoice.objects.filter(date__range=[start_date, end_date]).order_by('date')

        # 建立回應與 csv writer
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="invoices_{start_date}_to_{end_date}.csv"'
        writer = csv.writer(response)
        
        # 寫入欄位名稱
        writer.writerow(['發票號碼', '日期', '發票類型', '廠商', '廠商統編','敘述', '發票金額', '稅額','銷項稅額總額','進項稅額總額',tax_label])

        # 寫入資料列
        for invoice in invoices:
            writer.writerow([invoice.invoice_number, invoice.date, invoice.invoice_type,invoice.partner,invoice.partner.partner_number,invoice.description,invoice.amount,invoice.tax_amount,"","",""])
        # 寫入總計
        writer.writerow(['總計','','','','','','','',total_ar_tax,total_ap_tax,tax])
        return response
    else:
        return redirect('invoice_list')  

def delete_invoice(request, invoice_id):
    invoice=Invoice.objects.get(id=invoice_id)
    if request.method=='POST':
        invoice.delete()
        messages.success(request,'成功刪除發票')
        return redirect('invoice_list')
    return render(request,'apar/delete_invoice.html',{
        'invoice':invoice
    })  

        


