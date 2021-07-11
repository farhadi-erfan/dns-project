from django.db import models


class Bank(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)

# Create your models here.
