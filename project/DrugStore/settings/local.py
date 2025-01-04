from DrugStore.settings.base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "drug_store",
        "USER": "mohsen",
        "PASSWORD": "better_one",
        "PORT": 5432,
        "HOST": "localhost",
    }
}

DEBUG = True

if DEBUG:
    
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    mimetypes.add_type("text/css", ".css", True)
