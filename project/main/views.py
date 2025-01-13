from io import BytesIO
import logging
import os
import weasyprint
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from copy import deepcopy
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from main.forms import BgtForm, LoanForm, SldForm, BgtEditForm, SldEdit, DrugEditForm
from main.models import Drug as Drg, Bgt as Bg, Loan, Note, Sld, BillSld, BillBgt
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.auth.decorators import permission_required, login_required
from django.db.transaction import atomic


# Create your views here.


def send_sld_pdf_email(bill_object):
    # sends a pdf of a bill with all its sld objects via email
    slds = bill_object.slds.all()
    html_str = render_to_string("sld/pdf_sld.html", {"slds": slds, "pdf": "ok"})
    bytes_io = BytesIO()
    weasyprint.HTML(string=html_str).write_pdf(
        bytes_io, stylesheets=[settings.STATIC_ROOT / "css/sld/pdf.css"]
    )
    # sending the email
    mail = EmailMessage(
        bill_object.customer,
        f"{bill_object.customer}'s purchases from ahmadyar shop",
        settings.EMAIL_HOST_USER,
        ["aliahmadyar10@gmail.com"],
    )
    mail.attach(
        f"{bill_object.customer}__{bill_object.number}.pdf",
        bytes_io.getvalue(),
        "attachment/pdf",
    )

    mail.send(fail_silently=False)

    return 1


def send_bgt_pdf_email(bill_object):
    # sends a pdf of bgts in a specific bill via email

    bgts = bill_object.bgts.all()
    html_str = render_to_string(
        "bgt/pdf_bgt.html",
        {
            "bgts": bgts,
            "pdf": "ok",
        },
    )
    bytes_io = BytesIO()
    weasyprint.HTML(string=html_str).write_pdf(
        bytes_io, stylesheets=[settings.STATIC_ROOT / "css/bgt/pdf.css"]
    )
    # sending the email
    mail = EmailMessage(
        bill_object.company,
        f"purchases from {bill_object.company}'s on {bill_object.date}",
        settings.EMAIL_HOST_USER,
        ["aliahmadyar10@gmail.com"],
    )

    mail.attach(
        f"{bill_object.company}__{bill_object.number}.pdf",
        bytes_io.getvalue(),
        "attachment/pdf",
    )

    mail.send(fail_silently=False)
    return 1


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def main_page(request, term=None):
    """
    this view renders main page for the admin users only.
    -- it handles search, infinit scrolling pagination and initial rendering

    """
    drugs = Drg.objects.filter(active=True).order_by("name")
    # if a search query is sent, handle searching it with trigram similarity algorithm
    if term:
        drugs = (
            Drg.objects.filter(active=True)
            .annotate(search=TrigramSimilarity("name", term))
            .filter(search__gt=0.2)
        )
        messages.success(request, "نتایج جستجو برای " + term)

    # pagination for infinit scrolling
    paginated = Paginator(drugs, 10)
    requested_page = None
    # if scrolled for next pages, a page value is received
    if "page" in request.GET:
        requested_page = request.GET["page"]
        try:
            page = paginated.page(requested_page)
        except EmptyPage:
            if "just_page" in request.GET:
                return HttpResponse("")
            page = paginated.page(paginated.num_pages)
        except PageNotAnInteger:
            page = paginated.page(1)
        return render(
            request,
            "main__/portion_list.html",
            {"pdf": None, "page": page, "pax": "home"},
        )
    # when the admin initially switches to home page
    else:
        page = paginated.page(1)
        return render(
            request,
            "main__/home.html",
            {
                "pdf": None,
                "pax": None,
                "user": request.user,
                "page": page,
                "pax": "home",
            },
        )


@login_required
@permission_required("main.purchase-perm", raise_exception=True)
def buy(request):
    drugs = [drug.name for drug in Drg.objects.all()]
    media_url = request.build_absolute_uri("/media/drugs/")
    if request.method == "POST":
        data = request.POST
        form = BgtForm(data, request.FILES)
        if form.is_valid():
            bgt = form.save(commit=False)

            try:
                drug = Drg.objects.get(unique=bgt.name + "&&" + bgt.company)
                with atomic():
                    bgt.drug = drug
                    drug.existing_amount += (
                        bgt.amount
                    )  # though we can get it by calling
                    bgt.save()
                    drug.save()

            except Drg.DoesNotExist:
                with atomic():
                    drug = Drg.objects.create(
                        name=bgt.name,
                        company=bgt.company,
                        photo=bgt.photo,
                        unique=bgt.name + "&&" + bgt.company,
                        existing_amount=bgt.amount,
                    )
                    bgt.drug = drug
                    bgt.save()
            existing_bill = BillBgt.objects.filter(number=bgt.bgt_bill)
            # setting the appropriate bill number for the sell object
            new_bill = None
            with atomic():
                if len(existing_bill) > 0:
                    existing_bill[0].bgts.add(bgt)
                else:
                    new_bill = BillBgt.objects.create(
                        number=bgt.bgt_bill,
                        company=bgt.company,
                        date=bgt.date.strftime("%y/%m/%d"),
                    )
                    new_bill.bgts.add(bgt)
                    new_bill.save()
            # sending
            # check if there are previous bill not sent by email
            not_sent = BillBgt.objects.filter(sent=False)
            for bill in not_sent:
                # discarding current item being added from being sent
                if (
                    len(existing_bill) > 0 and existing_bill[0].number == bill.number
                ) or (new_bill and new_bill.number == bill.number):
                    continue
                send_bgt_pdf_email(bill)
                bill.sent = True
                bill.save()
            messages.success(request, "جزئیات خرید موفقانه ثبت گردید.")
            return render(
                request,
                "bgt/bgt.html",
                {
                    "form": BgtForm(data=request.POST),
                    "media_url": media_url,
                    "errors": None,
                    "edit": None,
                    "drugs": drugs,
                },
            )
        else:
            # there is an error
            messages.error(request, "خطا در ثبت معلومات!")
            return render(
                request,
                "bgt/bgt.html",
                {
                    "pdf": None,
                    "pax": None,
                    "form": form,
                    "drugs": drugs,
                    "edit": None,
                    "media_url": media_url,
                    "errors": form.errors,
                },
            )
    else:
        form = BgtForm()
    return render(
        request,
        "bgt/bgt.html",
        {
            "pdf": None,
            "pax": None,
            "errors": None,
            "edit": None,
            "form": form,
            "drugs": drugs,
            "media_url": media_url,
        },
    )


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def all_drugs(request):
    """sends the names of the drugs through fetch for select element"""
    if not "company" in request:
        drugs = [drug.name for drug in Drg.objects.all()]
        return JsonResponse(drugs, safe=False)
    else:
        companies = [
            drug.company
            for drug in Drg.objects.filter(name=str(request["name"]).title())
        ]
        return JsonResponse(
            companies, safe=False
        )  # safe false because we are sending something rather than dict(list)


@login_required
@permission_required("main.sale-perm", raise_exception=True)
def sell(request, id):
    media_url = request.build_absolute_uri("/media/drugs/")
    selected_bgt = Bg.objects.get(id=id)
    if selected_bgt.baqi_amount < 1:
        # no drugs exists of this type
        return render(
            request,
            "sld/success.html",
            {
                "selected_bgt": selected_bgt,
                "no_baqi": True,
                "pdf": None,
                "pax": None,
            },
        )
    if request.method == "POST":
        """save the image,"""
        form = SldForm(request.POST, request.FILES)
        if form.is_valid():
            try:

                # pre saving sld
                sld_obj = form.save(commit=False)
                # getting form data

                cd = form.cleaned_data
                # finding the drug, its bgt and date| assiging bgt and drug objects to current sld
                # making it atomic
                with atomic():
                    bgt = Bg.objects.get(id=request.POST["bgt_id"])
                    drug = Drg.objects.get(id=bgt.drug.id)
                    sld_obj.drug = drug
                    sld_obj.bgt = bgt

                    # profite calculation
                    sld_obj.profite = (sld_obj.price - bgt.price) * sld_obj.amount
                    # bgt object remaining amount calculations,
                    drug.existing_amount -= sld_obj.amount
                    bgt.sld_amount += sld_obj.amount
                    bgt.baqi_amount -= cd["amount"]
                    bgt.save()
                    drug.save()
                    sld_obj.save()

            except Exception as e:
                messages.error(request, "خطا در ثبت فروش!")
                logObjec = logging.getLogger("print_logger")
                logObjec.info(str(form.errors))
                return render(
                    request,
                    "sld/sld.html",
                    {
                        "pdf": None,
                        "pax": None,
                        "form": form,
                        "instance": selected_bgt,
                        "media_url": media_url,
                        "errors": form.errors,
                    },
                )

            # bill management
            existing_bill = BillSld.objects.filter(number=sld_obj.sld_bill)
            # setting the appropriate bill number for the sell object
            new_bill = None
            if len(existing_bill) > 0:
                existing_bill[0].slds.add(sld_obj)
            else:
                new_bill = BillSld.objects.create(
                    number=sld_obj.sld_bill,
                    customer=sld_obj.customer,
                    date=sld_obj.date.strftime("%y/%m/%d"),
                )
                new_bill.slds.add(sld_obj)
                new_bill.save()
            # sending
            # check if there are previous bill not sent by email
            not_sent = BillSld.objects.filter(sent=False)
            for bill in not_sent:
                # discarding current item being added from being sent
                if (
                    len(existing_bill) > 0 and existing_bill[0].number == bill.number
                ) or (new_bill and new_bill.number == bill.number):
                    continue
                try:
                    send_sld_pdf_email(bill)
                    bill.sent = True
                    bill.save()
                except:
                    bill.sent = False
                    bill.save()

            # preparing drugs for next sld form
            drugs = [drug.name for drug in Drg.objects.all()]
            messages.success(request, "جزئیات فروش موفقانه ثبت گردید.")
            return render(
                request,
                "sld/success.html",
                {
                    "no_baqi": False,
                    "pdf": None,
                    "pax": None,
                },
            )
        else:
            # there are form errors
            errors = form.errors
            # errors = form.error_class.as_text(form.errors).split("\n")[1:]  # taking out erros
            messages.error(request, "خطا در ثبت فروش!")
            logObjec = logging.getLogger("print_logger")
            logObjec.error("There was an error while saving sld->", errors)
            return render(
                request,
                "sld/sld.html",
                {
                    "pdf": None,
                    "pax": None,
                    "form": form,
                    "media_url": media_url,
                    "errors": errors,
                    "instance": selected_bgt,
                },
            )
    else:
        form = SldForm()
        return render(
            request,
            "sld/sld.html",
            {
                "pdf": None,
                "pax": None,
                "form": form,
                "media_url": media_url,
                "qrcode": True,
                "instance": selected_bgt,
            },
        )


@login_required
@permission_required("main.purchase-perm", raise_exception=True)
def get_drug_bgts(request):
    """sends bgt details for sell template in bgt selector"""
    drug_name = request.GET["drug_name"]
    company = request.GET["company"]
    bgts = Bg.objects.filter(name=drug_name, company=company, available=True)
    bgts = [
        (drug.price, drug.baqi_amount, str(drug.date), drug.currency) for drug in bgts
    ]
    return JsonResponse(bgts, safe=False)


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def get_drug_companies(request):
    drug_name = request.GET["drug_name"]
    drug_name = drug_name.title()
    companies = [drug.company for drug in Drg.objects.filter(name=drug_name)]
    return JsonResponse(safe=False, data=companies)


@login_required
@permission_required("main.sale-perm", raise_exception=True)
def send_sld_photo(request):
    data = request.GET
    name = data["name"]
    company = data["company"]
    drug = Drg.objects.get(name=name, company=company)
    return HttpResponse(drug.photo.url)


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def show_drug_detail(request, name, company):
    name = name.title()
    company = company.title()
    drug = Drg.objects.get(name=name, company=company)
    return render(
        request, "drug/drug_detail.html", {"pdf": None, "pax": None, "drug": drug}
    )


@login_required
@permission_required("main.purchase-perm", raise_exception=True)
def show_bgt_detail(request, name, company, date):
    name = name.title()
    company = company.title()
    unique = name + "&&" + company + "&&" + date
    bgt = Bg.objects.get(unique=unique)
    drug = Drg.objects.get(name=name, company=company)
    return render(
        request,
        "bgt/bgt_detail.html",
        {"pdf": None, "pax": None, "bgt": bgt, "drug": drug},
    )


@login_required
@permission_required("main.sale-perm", raise_exception=True)
def show_sld_detail(request, name, company, date, customer):
    name = name.title()
    customer = customer.title()
    unique = name + "&&" + company + "&&" + date + "&&" + customer
    sld = Sld.objects.get(unique=unique)
    drug = Drg.objects.get(name=name, company=sld.company)
    return render(
        request,
        "sld/sld_detail.html",
        {"pdf": None, "pax": None, "sld": sld, "drug": drug},
    )


@login_required
@permission_required("main.purchase-perm", raise_exception=True)
def edit_bgt(request, name, company, date):
    """
    things to cnsider here
    * drug uniqe , name , existing amount could change since being update
    * bgt bqi and uniques + could be change
    """
    data = request.POST
    pre_bgt_unique = name + "&&" + company + "&&" + date
    pre_bgt = deepcopy(Bg.objects.get(unique=pre_bgt_unique))
    pre_drug = deepcopy(pre_bgt.drug)
    if request.method == "POST":
        bgt_edit_form = BgtEditForm(
            files=request.FILES, instance=deepcopy(pre_bgt), data=data
        )
        drug_edit_form = DrugEditForm(
            files=request.FILES, instance=deepcopy(pre_drug), data=data
        )
        if bgt_edit_form.is_valid() and drug_edit_form.is_valid():
            new_bgt = bgt_edit_form.save(commit=False)
            new_drug = drug_edit_form.save(commit=False)
            # making it atomic
            try:
                with atomic():
                    new_drug.existing_amount = (
                        pre_drug.existing_amount - pre_bgt.amount + new_bgt.amount
                    )
                    new_bgt.baqi_amount += new_bgt.amount - pre_bgt.amount
                    new_drug.save()
                    new_bgt.drug = new_drug
                    new_bgt.save()
                messages.success(request, "تغییرات موفقانه ثبت گردید.")
            except Exception as e:
                logger = logging.getLogger("print_logger")
                logger.error("There was an error editing bgt:" + str(e))
                return render(
                    request,
                    "bgt/bgt.html",
                    {
                        "form": bgt_edit_form,
                        "edit": "1",
                        "instance": instance,
                    },
                )
            return redirect(new_bgt.get_absolute_url())
        else:
            logger = logging.getLogger("print_logger")
            logger.error(
                "There was a validation error in form in bgt edit: "
                + str(bgt_edit_form.errors)
            )
            return render(
                request,
                "bgt/bgt.html",
                {
                    "form": bgt_edit_form,
                    "edit": "1",
                    "instance": instance,
                },
            )

    else:
        unique = name + "&&" + company + "&&" + date
        instance = Bg.objects.get(unique=unique)
        bgt_edit_form = BgtEditForm(instance=instance)
        return render(
            request,
            "bgt/bgt.html",
            {
                "form": bgt_edit_form,
                "edit": "1",
                "instance": instance,
            },
        )


@login_required
@permission_required("main.sale-perm", raise_exception=True)
def edit_sld(request, name, company, date, customer):
    pre_unique = name + "&&" + company + "&&" + date + "&&" + customer
    pre_sld = deepcopy(Sld.objects.get(unique=pre_unique))
    if request.method == "POST":
        sld_edit_form = SldEdit(
            instance=Sld.objects.get(unique=pre_unique), data=request.POST
        )
        if sld_edit_form.is_valid():
            new_sld = sld_edit_form.save(commit=False)
            # calculating the existing amount both for drug and bgt
            try:
                with atomic():
                    bgt_baqi = pre_sld.bgt.baqi_amount
                    new_sld.drug.existing_amount = (
                        pre_sld.drug.existing_amount + pre_sld.amount - new_sld.amount
                    )
                    new_sld.bgt.baqi_amount = bgt_baqi + pre_sld.amount - new_sld.amount
                    new_sld.bgt.sld_amount = (
                        new_sld.bgt.amount - new_sld.bgt.baqi_amount
                    )
                    new_sld.bgt.save()
                    new_sld.drug.save()
                    new_sld.save()

            except Exception as e:
                logger = logging.getLogger("print_logger")
                logger.error("There was an error editing sld:" + str(e))
                return render(
                    request,
                    "sld/sld.html",
                    {
                        "pdf": None,
                        "pax": None,
                        "form": sld_edit_form,
                        "instance": pre_sld,
                        "edit": "1",
                    },
                )
            # pre_sld.delete() ---> does not work since memory reference are the same
            return redirect(new_sld.get_absolute_url())
        else:
            logger = logging.getLogger("print_logger")
            logger.error(
                "There was a validation error in form in sld edit: "
                + str(sld_edit_form.errors)
            )

            return render(
                request,
                "sld/sld.html",
                {
                    "pdf": None,
                    "pax": None,
                    "form": sld_edit_form,
                    "instance": pre_sld,
                    "edit": "1",
                },
            )
    else:
        sld_edit_form = SldEdit(instance=pre_sld)
        return render(
            request,
            "sld/sld.html",
            {
                "form": sld_edit_form,
                "instance": pre_sld,
                "edit": "1",
            },
        )


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def delete(request, name, company, date=None, customer=None):
    if customer:  # sld deletion
        Sld.objects.get(
            name=name, company=company, date=date, customer=customer
        ).delete()
        return redirect(reverse("main:show_list", args=["sld"]))
    elif date:  # bgt deleiton
        bgt = Bg.objects.get(name=name, company=company, date=date)
        drug = Drg.objects.get(name=name, company=company)
        # deleting related slds
        if (
            hasattr(drug.bgts) and len(drug.bgts.all()) == 1
        ):  # if it is the only remaining bgt
            drug.delete()  # deletes both drug and bgt and sld
        elif (
            hasattr(drug.bgts) and len(drug.bgts.all()) > 1
        ):  # if it is one of the collection
            bgt.delete()
            for sld in Sld.objects.filter(bgt=bgt):
                sld.delete()
        return redirect(reverse("main:show_list", args=["bgt"]))
    else:  # Drug deleltion
        Drg.objects.get(name=name, company=company).delete()
        return redirect("main:main")


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def show_list(request, list_type, term=None):
    """
    note: pax means which page type is it, we did this since we are extending base.html,
    so that  searching be determined well
    """
    data = request.GET
    # handling sorting type
    sort_type = data.get("sort_by", None)
    if sort_type:
        previous = request.session[sort_type]
        if "-" in previous:
            request.session[sort_type] = request.session[sort_type][1:]
        else:
            request.session[sort_type] = "-" + request.session[sort_type]
        request.session.modified = True
        sort_type = request.session[sort_type]
    else:
        # initializign the sortings
        request.session["name"] = "name"
        request.session["company"] = "company"
        request.session["date"] = "date"
        if list_type == "bgt":
            request.session["bill"] = "bgt_bill"
        else:
            request.session["bill"] = "sld_bill"
        sort_type = "-date"
    # handling list type to show
    if list_type == "bgt":
        bgts = Bg.objects.all().order_by(sort_type)
        # handling search
        if term:
            messages.success(request, "نتایج جستجو برای " + term)
            bgts = Bg.objects.annotate(search=TrigramSimilarity("name", term)).filter(
                search__gt=0.2
            )
        # if a bill number is given, show specifc bgts according to it
        bill_num = data.get("bill", None)
        if bill_num:
            bgts = bgts.filter(bgt_bill=bill_num)

        return render(
            request, "bgt/list.html", {"pdf": None, "bgts": bgts, "pax": "bgts"}
        )
    else:
        slds = Sld.objects.all().order_by(sort_type)
        # handling search
        if term:
            messages.success(request, "نتایج جستجو برای " + term)
            slds = slds.annotate(search=TrigramSimilarity("name", term)).filter(
                search__gt=0.2
            )
        # if a bill number is given, show specifc slds according to it
        bill_num = data.get("bill", None)
        if bill_num:
            slds = slds.filter(sld_bill=bill_num)
        return render(
            request, "sld/list.html", {"pdf": None, "slds": slds, "pax": "slds"}
        )


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def show_specific(request, list_type):
    """
    This view returns bgts or slds of a specific drug
    """
    data = request.GET["data"].split("&&")
    name, company = data[0], data[1]
    if list_type == "bgt":
        bgts = Bg.objects.filter(name=name, company=company).order_by("-date")
        return render(request, "bgt/list.html", {"bgts": bgts})
    else:
        slds = Sld.objects.filter(name=name, company=company).order_by("-date")
        return render(request, "sld/list.html", {"slds": slds})


@login_required
@permission_required("main.drug-perm", raise_exception=True)
def search(request, type_):
    term = request.POST.get("term", None)
    if type_ == "home":
        return redirect(reverse("main:main_search", args=[term]))
    elif type_ == "bgts":
        return redirect(reverse("main:show_list_search", args=["bgt", term]))
    else:
        return redirect(reverse("main:show_list_search", args=["sld", term]))


@login_required
@permission_required("main.sale-perm", raise_exception=True)
def balance(request, month=None, year=None):
    months_name = {
        1: "حمل",
        2: "ثور",
        3: "جوزا",
        4: "سرطان",
        5: "اسد",
        6: "سنبله",
        7: "میزان",
        8: "عقرب",
        9: "قوس",
        10: "جدی",
        11: "دلو",
        12: "حوت",
    }
    if not (month and year):
        slds = Sld.objects.order_by("date")
        years = set([sld.date.year for sld in slds])
        data = (
            []
        )  # 0-year_number       1-total_year_prof       2-every months-profs for every year
        for year in years:
            # traversing over every year
            # this filtering does not work, since the year attribute is not an integer
            # this_year_slds = slds.filter(date__year=year)
            # print(slds,"------------ssssless================")
            this_year_slds = [s for s in slds if int(s.date.year) == year]
            this_year_profs = 0
            months = set([sld.date.month for sld in this_year_slds])
            months_profs = []
            for month in months:
                # traversing over months of this year and summing up the profits
                # does not work since month attribute is not an integer
                # this_month_slds = this_year_slds.filter(date__month=month)
                this_month_slds = [
                    s for s in this_year_slds if int(s.date.month) == month
                ]
                this_month_profs = 0
                for s in this_month_slds:
                    this_month_profs += int(s.profite)

                months_profs.append([months_name[month], this_month_profs, 0])
                this_year_profs += this_month_profs
            max_month = max([m[1] for m in months_profs])
            for month in months_profs:
                month[2] = month[1] * 360 / max_month
            data.append([year, this_year_profs, months_profs])
        data = reversed(data)
    return render(
        request, "finance/profs.html", context={"pdf": None, "pax": None, "profs": data}
    )


@login_required
@require_POST
@permission_required("main.note-perm", raise_exception=True)
def delete_note(request):
    data = request.POST
    notes = list(data.keys())[1:]
    note_ids = [int(data[id_]) for id_ in notes]
    Note.objects.filter(id__in=note_ids).delete()
    return redirect("main:notes_list_all")


class NotesList(
    LoginRequiredMixin, ListView, TemplateResponseMixin, PermissionRequiredMixin
):
    """this is a CBV that also includes pagination"""

    permission_required = "main.note-perm"
    model = Note
    paginate_by = 8
    context_object_name = "notes"
    template_name = "finance/notes.html"

    def get(self, request, page=None, *args, **kwargs):

        if page:
            object_list = self.get_queryset()
            try:
                self.page = self.paginate_queryset(object_list, page)
            except Exception:
                return HttpResponse("")
            # self.page[2] is equal to object_list attribute of the page
            items = [item for item in self.page[2].values()]
            return render(
                request,
                "finance/notes_partial.html",
                context={"pdf": None, "pax": None, "notes": items, "page_number": page},
            )
        return super().get(request, *args, **kwargs)


class CreateNote(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    permission_required = "main.note-perm"
    model = Note
    fields = ["title", "importance", "content"]
    success_url = reverse_lazy("main:notes_list_all")
    template_name = "finance/create_edit_note.html"


class UpdateNote(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    permission_required = "main.note-perm"
    model = Note
    fields = ["title", "importance", "content"]
    success_url = reverse_lazy("main:notes_list_all")
    template_name = "finance/create_edit_note.html"


@permission_required("main.purchase-perm")
@login_required
def manage_loan(request, id=None):
    """this view handles deletion and creation of a load"""
    instance = Loan.objects.filter(id=id).first() if id else None
    if request.method == "GET":
        form = LoanForm()
        edit = False
        if instance:
            form = LoanForm(instance=instance)
            edit = True
        return render(
            request,
            "loan/create_loan.html",
            {"form": form, "edit": edit, "instance": instance},
        )
    else:
        form = LoanForm(data=request.POST, files=request.FILES)
        if instance:
            form = LoanForm(data=request.POST, instance=instance, files=request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            # duplicate prevention
            check = Loan.objects.filter(
                client_name=cd["client_name"],
                date=cd["date"],
                amount=cd["amount"],
            ).exists()

            if not check:
                obj = form.save(commit=False)
                if instance:
                    obj.client_id = instance.client_id
                else:
                    # a new is being created, so taking files from FILES attribute of requestszzzzzz
                    obj.client_id = request.FILES["client_id"]
                obj.save()

            return redirect("main:list_loans")
        else:
            return render(
                request, "loan/create_loan.html", {"form": form, "errors": form.errors}
            )


@login_required
def list_loans(request):
    loans = Loan.objects.all()
    return render(request, "loan/list.html", {"loans": loans})


@permission_required("main.purchase-perm", raise_exception=True)
@login_required
def read_qr_sell(request):
    return render(request, "sld/pre_sel_qr.html", context={"pax": None, "pdf": None})


@permission_required("main.purchase-perm", raise_exception=True)
@login_required
def read_logs(request):
    log_file_path = os.path.join(settings.BASE_DIR, "logging/info.log")
    logs = ""
    with open(log_file_path, "r") as f:
        logs = f.read()

    return HttpResponse(logs)
