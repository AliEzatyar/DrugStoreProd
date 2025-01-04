from django.db import models


# Create your models here.
class Prof(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(null=True,upload_to="Owners/")
    phone = models.CharField(max_length=12,default="No Number")
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Profile"


