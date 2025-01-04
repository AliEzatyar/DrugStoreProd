import os
from django.db import models
from datetime import date
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
from DrugStore.settings.base import DR_MOHSEN_ID
# Create your models here.
# not a good technique
# Ali_Ahmadyar = User.objects.get(username="Ali_Ahmadyar")


class Drug(models.Model):
    name = models.CharField(max_length=25, default="بدون نام")
    company = models.CharField(max_length=25)
    existing_amount = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    photo = models.ImageField(upload_to='drugs/', null=True, default="static\\UsedPhoto\\BedonAks.jpg")
    description = models.TextField(blank=True, default="بدون جزئیات")
    unique = models.CharField(max_length=60, blank=True, default="no name and company", unique=True)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['name']),
            models.Index(fields=['company'])
        ]
        ordering = ['name', '-created']

    def __str__(self):
        return f"دارو با نام : {self.name} و با تعداد موجودی {self.existing_amount}"

    def get_absolute_url(self):
        return reverse("main:show_drug_detail", args=[self.name, self.company])


class BillSld(models.Model):
    # represents a bill of sld 
    sent = models.BooleanField(default=False)
    customer = models.CharField(max_length=60)
    date = models.CharField(max_length=60)
    number = models.IntegerField()


class BillBgt(models.Model):
    # represents a bill of bgt
    sent = models.BooleanField(default=False)
    date = models.CharField(max_length=60)
    number = models.IntegerField()
    company = models.CharField(max_length=60, default="default-company")


class Bgt(models.Model):
    Buyer = models.ForeignKey(User, default=DR_MOHSEN_ID, on_delete=models.CASCADE, related_name="purchases")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='Purchases', blank=True)
    name = models.CharField(max_length=25, default='بدون نام')
    company = models.CharField(max_length=25, default='بدون شرکت')
    price = models.DecimalField(default=0, decimal_places=1, max_digits=10)
    amount = models.DecimalField(default=0, decimal_places=0, max_digits=10)
    created = jmodels.jDateTimeField(auto_now_add=True)
    date = jmodels.jDateField(default=jmodels.timezone.now())
    expire_months = models.SmallIntegerField(default=30)
    photo = models.ImageField(upload_to='drugs', null=True, blank=True)
    bgt_bill = models.PositiveSmallIntegerField(verbose_name="bill", default=0)
    unique = models.CharField(blank=True, unique=True, max_length=100)
    sld_amount = models.DecimalField(default=0, decimal_places=0, max_digits=10,
                                     blank=True)  # this field increase in every sold
    baqi_amount = models.DecimalField(default=0, decimal_places=0, max_digits=10, blank=True)
    total = models.DecimalField(default=0, decimal_places=1, max_digits=10)
    available = models.BooleanField(default=True)
    bill_object = models.ForeignKey('main.BillBgt', on_delete=models.CASCADE, related_name="bgts", default=1)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['company']),
            models.Index(fields=['-date'])
        ]
        ordering = ['-name']
        verbose_name = "Purchase"

    def __str__(self):
        return f"{str(self.date)}|{self.amount}x|{self.price}"

    def get_absolute_url(self):
        return reverse('main:show_bgt_detail', args=[self.name, self.company, str(self.date)])


class Sld(models.Model):
    seller = models.ForeignKey(User, default=DR_MOHSEN_ID, on_delete=models.CASCADE, related_name="sales")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE,
                             related_name='slds')  # we should also take out its bgts using this filed
    bgt = models.ForeignKey(Bgt, on_delete=models.CASCADE, related_name="sales", verbose_name="Purchase")
    name = models.CharField(default='بدون نام', max_length=30)
    amount = models.DecimalField(default=0, decimal_places=0, max_digits=10)
    price = models.DecimalField(default=0, decimal_places=1, max_digits=10)
    created = jmodels.jDateTimeField(auto_now_add=True)
    date = jmodels.jDateField(default=jmodels.timezone.now())
    company = models.CharField(default='بدون شرکت', max_length=30)
    customer = models.CharField(default="نا مشخص", max_length=30)
    profite = models.DecimalField(blank=True, decimal_places=1, max_digits=10)
    sld_bill = models.IntegerField(verbose_name="bill", default=0)
    unique = models.CharField(blank=True, max_length=100, unique=True)
    total = models.DecimalField(default=0, decimal_places=1, max_digits=10)
    bill_object = models.ForeignKey("main.BillSld", on_delete=models.CASCADE, related_name="slds",
                                    default=1)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-date'])
        ]
        ordering = ['-date']
        verbose_name = "Sale"

    def __str__(self):
        return f"{self.name} با تعداد {self.amount} فروش "

    def get_absolute_url(self):
        return reverse('main:show_sld_detail', args=[self.name, self.company, self.date, self.customer])

class Note(models.Model):
    title = models.CharField(max_length=100,verbose_name="عنوان",unique=True)
    author = models.ForeignKey('auth.User',default=DR_MOHSEN_ID,on_delete=models.CASCADE,related_name="notes")
    content = models.TextField(verbose_name="محتوای یادداشت")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now = True)
    importance = models.PositiveSmallIntegerField(verbose_name="اولویت",choices=[(1,'very important'),(2,"important"),(3,'Easy')])
    class Meta:
        ordering = ['importance']


@receiver(pre_save, sender=Sld)
def before_sld_save(*args, **kwargs):
    print("before saving ")


@receiver(post_save, sender=Sld)
def after_sld_save(*args, **kwargs):
    print("after saving")
