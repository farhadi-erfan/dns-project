from django.db import models


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


class Buyer(SingletonModel):
    name = models.CharField(max_length=20, null=True, blank=True)
    public_key = models.TextField(null=True)
    private_key = models.TextField(null=True)
    certificate = models.TextField(null=True)
