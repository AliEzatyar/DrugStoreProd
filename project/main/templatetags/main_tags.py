from django import template
from ..models import Sld, Bgt

register = template.Library()


@register.simple_tag(name="last_sld")
def last_sale(drug_name, company):
    sales = Sld.objects.filter(name=drug_name, company=company).order_by('-date')
    if len(sales) > 0:
        sale = sales[0]
        return sale
    else:
        return None

@register.simple_tag(name="last_bgt")
def last_bgt(drug_name, company):
    bgts = Bgt.objects.filter(name=drug_name,company=company)
    if len(bgts)>0:
        bgt = bgts.order_by("-date")[0]
        return bgt
    else:
        return None

@register.filter(name="forloop_index")
def index_value(year,index):
    return year[index]


@register.filter(name="list_slice")
def slice(arr,parts):
    parts = parts.split(",")
    # print("\n",parts,len(arr),"+",arr[int(parts[0])],"00000000000000000000000000000000000000")
    return list(arr)[int(parts[0]):int(parts[1])]



