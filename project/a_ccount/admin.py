from django.contrib import admin

# Register your models here.
from a_ccount.models import Prof


@admin.register(Prof)
class prof_admin(admin.ModelAdmin):
    list_display = ['user','created']
