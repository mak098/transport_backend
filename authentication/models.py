from django.db import models

from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):

    phone_number =models.CharField(max_length=15,null=True, verbose_name= "Phone number")
    class meta:
        app_label = "Users"
        db_table = "users"


class TemporaryUser(models.Model):
    
    phone_number = models.CharField(max_length=50, unique=True)
    otp = models.CharField(max_length=10, default='', blank=True)
    record_at = models.DateTimeField(auto_now=True)
    recovery_token = models.CharField(max_length=50, null=True)
    bad_code_count = models.IntegerField(default=0, blank=True)
    bad_code_init_time = models.DateTimeField(auto_now_add=True)