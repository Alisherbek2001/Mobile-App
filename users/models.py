from django.contrib.auth.models import AbstractUser,UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _



class User(AbstractUser):
    birth_date = models.DateField(_("birth date"),null=True,blank=True)
    gender = models.CharField(_("gender"),max_length=255,null=True,blank=True)
    birth_country = models.CharField(_("birth country"),max_length=255,null=True,blank=True)
    current_country = models.CharField(_("current country"),max_length=255,null=True,blank=True)
    
    objects = UserManager()
    
    def __str__(self) -> str:
        return self.username
    
