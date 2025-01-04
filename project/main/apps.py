import os
import time
#
import schedule
from django.apps import AppConfig
from django.core.signals import request_started
from django.dispatch import receiver

from DrugStore import settings


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    def ready(self):
        os.environ["PATH"] = r'C:\Program Files\GTK3-Runtime Win64\bin' + os.pathsep+ os.environ.get("PATH","")
        print("--------------------------")
        # from .signals import started, created,finished
        from .signals import bgt_deletion,sld_deletion,drug_deletion
        # def delete_photos():
        #     os.chdir(settings.MEDIA_ROOT+"drugs/")
        #     photos = os.listdir(os.getcwd())
        #     from main.models import Drug
        #     for drug in Drug.objects.all():
        #         potos= [f for f in photos if ("_".join(drug.name.split()) in f  and "_".join(drug.company.split()) in f)]
        #         potos.sort(key=lambda x: os.path.getctime(x),reverse=True)
        #         for i in range(2,len(potos)):
        #             os.remove(potos[i])
        #         # print(f"potos --{drug.name + drug.company}--> ",potos)
        #
        # @receiver(request_started)
        # def scedule(*args, **kwargs):
        #     # print(" a request was made")
        #     delete_photos()