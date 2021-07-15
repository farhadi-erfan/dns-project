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


class BlockChain(SingletonModel):
    name = models.CharField(max_length=20, null=True, blank=True)
    public_key = models.TextField(null=True)
    private_key = models.TextField(null=True)
    certificate = models.TextField(null=True)


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
