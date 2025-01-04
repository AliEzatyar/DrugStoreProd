from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.forms import ValidationError

# Create your views here.
from a_ccount.forms import LoginForm

"""
    next comes from login_required and in template we say 'request.GET.next'
"""


def login_user(request):
    errors = None
    if request.method == "POST":
        data = request.POST
        logForm = LoginForm(data)
        if logForm.is_valid():
            cd = logForm.cleaned_data
            try:
                user = User.objects.get(username=cd['username'])
                if user and user.check_password(cd['password']):
                    login(request, user)
                    if data['next'] == "":
                        return redirect("main:main")
                    return redirect(to=data['next'])
                else:
                    errors = ValidationError('Password wrong! :)')
            except User.DoesNotExist:
                errors = ValidationError('User does not exist')
    else:  # get method
        logForm = LoginForm()
    return render(request, 'registration/login.html', {'logForm': logForm, 'errors': errors})


def log_out_user(request):
    logout(request)
    return render(request, 'registration/log_out.html')
