from django.urls import path

from a_ccount import views

app_name ='a_ccount'

urlpatterns =[
    path('login/',views.login_user,name='login_user'),
    path('logout/',views.log_out_user,name='log_out'),
]