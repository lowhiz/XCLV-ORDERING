# admin_auth/models.py
from django.db import models
from django.contrib.auth.hashers import make_password

class AdminUser(models.Model):
    admin_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    def __str__(self):
        return self.admin_id
