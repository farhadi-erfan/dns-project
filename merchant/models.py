from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Merchant(SingletonModel):
    name = models.CharField(max_length=20, null=True, blank=True)
    public_key = models.TextField(null=True)
    private_key = models.TextField(null=True)
    certificate = models.TextField(null=True)
    token = models.TextField(null=True)


class Transaction(models.Model):
    class Status(models.IntegerChoices):
        SUCCESS = 0, _('success')
        FAILURE = 1, _('failure')
        IN_PROGRESS = 2, _('in progress')

    buyer = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveBigIntegerField()
    status = models.IntegerField(choices=Status.choices, default=Status.IN_PROGRESS)
