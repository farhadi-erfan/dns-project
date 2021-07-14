from django.db import models


# Create your models here.
class Delegation(models.Model):
    user = models.TextField()
    delegated_to = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveBigIntegerField()
    current_value = models.PositiveBigIntegerField()
    count = models.IntegerField()
    time = models.DateTimeField()
    nonce = models.FloatField()


class Exchange(models.Model):
    sender = models.TextField()
    receiver = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    delegation = models.ForeignKey(to='Delegation', on_delete=models.PROTECT)
    amount = models.PositiveBigIntegerField()
    nonce = models.FloatField()
