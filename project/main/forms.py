from copy import deepcopy
from logging import getLogger, info
from django import forms
from django.core.exceptions import ValidationError
from main.models import Bgt, Drug
from main.models import Sld


class BgtForm(forms.ModelForm):
    class Meta:
        model = Bgt
        fields = [  # fields which are not shown in template, 1- drug,2- sld_amount, 3- date, 4- unique
            "name",
            "amount",
            "price",
            "company",
            "date",
            "photo",
            "bgt_bill",
            "total",
        ]

    def clean_total(self):
        total = self.cleaned_data['total']
        return abs(total)

    def clean_bgt_bill(self):
        bill = self.cleaned_data['bgt_bill']
        return abs(bill)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        return abs(amount)

    def clean_price(self):
        price = self.cleaned_data['price']
        return abs(price)

    def clean_name(self):
        name = self.cleaned_data['name']
        return name.title()

    def clean_company(self):
        company = self.cleaned_data['company']
        return company.title()

    def clean(self):
        cd = super().clean()
        """raising validation errors"""
        # print(cd)
        name = cd['name']
        if name == "انتخاب دارو":
            raise ValidationError("لطفا نام دارو را درج کنید")

        company = self.cleaned_data['company']
        if company in "انتخاب شرکت":
            raise ValidationError("لطفا شرکت دارو را درج کنید")

        amount = int(cd['amount'])
        if amount == 0 or amount > 10000:
            raise ValidationError("مقدار خرید منطقی نیست")

        price = int(cd['price'])
        if price > 15000 or price == 0:
            raise ValidationError('قیمت خرید منطقی نیست')

        bill = int(cd['bgt_bill'])
        if bill == 0:
            raise ValidationError("بیل نمبر درست نیست")

        unique = cd['name'].title() + "&&" + cd['company'].title() + "&&" + str(cd['date'])
        if Bgt.objects.filter(unique=unique).count() > 0:
            raise ValidationError("این خرید قبلا ثبت شده است")
        return cd

    def save(self, commit=True):
        """
            creating the unique, filling drug foriegnKey,evaluating baqi capitalizing drug name and company
        """
        cd = self.cleaned_data
        bgt = super().save(commit=False)
        bgt.baqi_amount = cd['amount']
        bgt.name = cd['name'].title()
        bgt.company = cd['company'].title()
        bgt.unique = bgt.name + "&&" + bgt.company + "&&" + str(cd['date'])
        # renaming image
        photo = cd['photo']
        """note: photos could be 2 type here, one is the default photo abs BedonAks, second: imageFiled object"""
        if type(photo) != str and photo != None:
            extension = str(photo.name).rsplit(".", 1)[1].lower()
            new_photo_name = bgt.name + "__" + bgt.company + "." + extension
            bgt.photo.name = new_photo_name
        if commit:
            bgt.save()
        return bgt


class SldForm(forms.ModelForm):
    bgt_detail = forms.CharField(max_length=50,required=False)
    bgt_id = forms.IntegerField(widget=forms.HiddenInput(),required=False)
    name = forms.CharField(max_length=60,widget=forms.HiddenInput,required=False)
    company = forms.CharField(max_length=60, widget=forms.HiddenInput, required=False)

    class Meta:
        model = Sld
        fields = [  # how to eclude??, excluded: drug,
            'amount', 'price','customer',
            'sld_bill','total', 'date',
            "bgt_id","name","company"
        ]

    def clean_total(self):
        total = self.cleaned_data['total']
        return abs(total)

    def clean_sld_bill(self):
        bill = self.cleaned_data['sld_bill']
        return abs(bill)

    def clean_customer(self):
        customer = self.cleaned_data['customer']
        return customer.title()

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        return abs(amount)

    def clean_price(self):
        price = self.cleaned_data['price']
        return abs(price)

    def clean(self):
        """in addition to clean, we are cleaning amount field for limiting max sale amount for a bgt"""
        cd = super().clean()

        # raising form errors if needed
        price = cd['price']
        if price > 15000 or price == 0:
            raise ValidationError("قیمت فروش منطقی نیست")

        # finding the bgt object to limit exact bgt over-amount selling
        lg = getLogger("print_logger")
        lg.info(f"-----------------bgt0d---{cd}")

        bgt_obj = Bgt.objects.get(id=int(cd["bgt_id"]))
        print("bgt fount ------------------------")
        # preventing repetition of the same sale
        sld_unique = bgt_obj.name + "&&" + str(cd['date']) + "&&" + cd['customer']
        if Sld.objects.filter(unique=sld_unique).count() > 0:
            raise ValidationError("این فروش قبلا ثبت شده است")

        # limiting max sale amount
        remaining = bgt_obj.amount - bgt_obj.sld_amount
        sale_amount = cd['amount']
        if sale_amount == 0:
            raise ValidationError("مقدار فروش نادرست")
        if remaining - sale_amount < 0:
            raise ValidationError(f"در خرید این دارو فقط{remaining} عدد باقی مانده است!")
        return cd

    def save(self, commit=True):
        """filling drug foriegnKey and creating unique"""
        cd = self.cleaned_data
        bgt_obj = Bgt.objects.get(id=int(cd["bgt_id"]))
        sld_obj = super().save(commit=False)
        sld_obj.unique = str(bgt_obj.name + "&&" + bgt_obj.company + "&&" + str(cd['date']) + "&&" + str(cd['customer']))

        print("before searching for drug......")
        print("uniquye made ...", sld_obj.name + "&&" + sld_obj.company)
        sld_obj.drug = Drug.objects.get(unique=sld_obj.name + "&&" + sld_obj.company)
        print("dru g fiubd......")
        if commit:
            sld_obj.save()
        return sld_obj


# THIS STRATEGY DOES NOT WORK
class DrugEditForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = ['name', 'company', 'photo']

    def clean_name(self):
        cd = self.cleaned_data
        return str(cd['name']).title()

    def clean_company(self):
        cd = self.cleaned_data
        return str(cd['company']).title()

    def save(self, commit=True):
        """makes the unique"""
        print(self.cleaned_data,"=+-+_+_++_++_+__")
        pre = deepcopy(Drug.objects.get(id=self.instance.id))
        pre_photo_name = pre.photo.name
        new_drug = super().save(commit=False)
        new_drug.unique = new_drug.name + "&&" + new_drug.company
        extension = str(new_drug.photo.name).rsplit(".", 1)[1].lower()
        if pre_photo_name != new_drug.photo.name and new_drug.photo.name != "":
            pre.photo.delete()
            print("deleted")
            new_drug.photo.name = "__".join(new_drug.unique.split("&&")) +"." +extension
        print(new_drug.photo.name,"new photo")
        if commit:
            new_drug.save()
        return new_drug


class BgtEditForm(forms.ModelForm):
    class Meta:
        model = Bgt
        fields = [
            'name', 'amount', 'price', 'company', 'date',
            'bgt_bill', 'total','expire_months'
        ]

    def clean_name(self):
        cd = self.cleaned_data
        name = cd['name'].title()
        return name

    def company(self):
        cd = self.cleaned_data
        company = cd['company'].title()
        return company

    def save(self, commit=True):
        new_bgt = super().save(commit=False)
        new_bgt.unique = new_bgt.name + "&&" + new_bgt.company + "&&" + str(new_bgt.date)
        if commit:
            new_bgt.save()
        return new_bgt


class SldEdit(forms.ModelForm):
    """name, company are not changeble in this form"""

    class Meta:
        model = Sld
        fields = [
            'amount', 'price', 'customer',
            'sld_bill', 'total', 'date'
        ]

    def clean_customer(self):
        return str(self.cleaned_data['customer']).title()

    def save(self, commit=True):
        new_sld = super().save(commit=False)
        """since we have got the instance before, we have the bgt related to this set before, so use it for calculating the profite"""
        # modifying unique, profite
        bgt = new_sld.bgt
        new_sld.profite = new_sld.amount * (new_sld.price - bgt.price)
        new_sld.unique = str(new_sld.name) + "&&" + str(new_sld.company) + "&&" + str(
            new_sld.date) + "&&" + new_sld.customer

        """note that existing amount both in bgt and drug objects are handled in view, since we have not the previous sld object """

        if commit:
            new_sld.save()
        return new_sld
