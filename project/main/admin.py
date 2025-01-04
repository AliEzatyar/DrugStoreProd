from django.contrib import admin
from django.contrib.auth.models import Permission
# Register your models here.
from a_ccount.models import Prof
from main.models import Drug, Bgt, Sld, BillSld, BillBgt


@admin.register(Bgt)
class BgtAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'price', 'amount','available', 'date', 'bill_object', 'unique']
    list_filter = ['date', 'company']
    ordering = [
        'name', 'bgt_bill', 'date'
    ]
    sortable_by = ['date','name','bgt_bill','amount']
    list_display_links = ["bill_object"]

@admin.register(Sld)
class SldAdmin(admin.ModelAdmin):
    list_display = ['name', 'company',"customer",'price', 'amount', 'date', 'bill_object',"bgt", 'unique']
    list_filter = [ 'date', 'company',"bgt"]
    ordering = ['name', 'date', 'sld_bill']
    sortable_by = ['date','name','sld_bill','amount']
    list_display_links = ["bill_object"]

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'description','existing_amount']
    list_filter = ['company']
    sortable_by = ['name','existing_amount']

admin.site.register(BillSld)
admin.site.register(BillBgt)
admin.site.register(Permission)