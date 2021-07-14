from django.db import models


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


class Bank(SingletonModel):
    name = models.CharField(max_length=20, null=True, blank=True)
    public_key = models.TextField(null=True)
    private_key = models.TextField(null=True)
    certificate = models.TextField(null=True)


class Account(models.Model):
    username = models.CharField(max_length=32)
    token = models.TextField(null=True)
    credit = models.PositiveBigIntegerField(default=0)


class Transaction(models.Model):
    source = models.ForeignKey(to='Account', on_delete=models.PROTECT, related_name='sent_transactions')
    destination = models.ForeignKey(to='Account', on_delete=models.PROTECT, related_name='received_transactions')
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    tid = models.CharField(max_length=64)
