from django.urls import path
from . import views

urlpatterns=[
    path("",views.index,name='index'),
    path("create/",views.create_invoice,name="create_invoice"),
    path("list/",views.invoice_list,name='invoice_list'),
    path("partner_list/",views.partner_list,name='partner_list'),
    path("payment_status/<int:invoice_id>/",views.payment_status,name='payment_status'),
    path("filter_date",views.filter_date,name='filter_date'),
    path("export_csv",views.export_csv,name="export_csv"),
    path("delete_invoice/<int:invoice_id>",views.delete_invoice,name="delete_invoice")

]